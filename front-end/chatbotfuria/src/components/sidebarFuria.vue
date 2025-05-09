<template>
  <div class="sidebar" :class="{ 'collapsed': !isExpanded, 'expanded-mobile': isMobileOpen }">

    <button 
      v-if="!isMobile" 
      class="toggle-btn btn btn-dark btn-sm" 
      @click="toggleSidebar"
    >
      <i :class="isExpanded ? 'bi bi-arrow-bar-left' : 'bi bi-arrow-bar-right'"></i>
    </button>

    <button 
    v-if="isMobileOpen && isMobile" 
    class="btn-close-mobile btn btn-light btn-sm align-self-end m-2" 
    @click="closeMobileSidebar"
  >
    <i class="bi bi-x-lg"></i>
  </button>

    <ul class="list-group p-3" v-if="isExpanded || isMobile">
  
      <p v-if="!isQuizPage" class="text-center fs-6 mt-5">
        <strong>Histórico de mensagens</strong>
      </p>

      <li 
        v-if="!isQuizPage"
        v-for="chat in recentChats" 
        :key="chat.id" 
        class="list-group-item chat-item p-2 m-2"
        @click="openChat(chat.id)"
      >
        {{ truncate(chat.summary, 20) }}
      </li>

      <li class="list-group-item new-chat mb-5 p-1 mt-auto">
        <button class="btn w-100 text-light" @click="handleNewChatOrRedirect">
          {{ isQuizPage ? "Ir para o ChatBot" : "+ Novo chat" }}
        </button>
      </li>
      <li class="list-group-item logout-item mb-5 p-1">
        <button class="btn w-100" @click="logout">Logout</button>
      </li>
    </ul>
  </div>
</template>

<script>

const baseURL = import.meta.env.VUE_APP_VITE_API_BASE;

export default {
  props: {
    visible: {
      type: Boolean,
      default: true,
    },
    isMobileOpen: {
    type: Boolean,
    default: false,
  },
  },
  data() {
    return {
      isExpanded: true,
      isMobile: false,
      recentChats: [], 
      userName: "",
    };
  },
  computed: {
    isQuizPage() {
      return this.$route.path === "/quiz/"; 
    },
  },
  methods: {
    closeMobileSidebar() {
      this.$emit('close-mobile');
    },
    openChat(chatId) {
      this.$router.push({ path: "/", query: { chatId } });
    },
    handleResize() {
      this.isMobile = window.innerWidth <= 768;
    },
    toggleSidebar() {
      this.isExpanded = !this.isExpanded;
    },
    async newChat() {
      this.$router.push({ path: "" });
    },
    handleNewChatOrRedirect() {
      if (this.isQuizPage) {
        this.$router.push("/"); 
      } else {
        this.newChat(); 
      }
    },
    truncate(text, maxLength) {
      if (!text) return "";
      return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
    },
    logout() {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      this.$router.push("/login");
    },
    async fetchRecentChats() {
  try {
    const token = localStorage.getItem('access');
    if (!token) {
      throw new Error('Nenhum token de acesso encontrado');
    }

    const response = await fetch(`${baseURL}/chat/recent-chats/`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      credentials: 'include' 
    });

    if (response.status === 401) {
      const refreshSuccess = await this.handleTokenRefresh();
      if (refreshSuccess) {
        return this.fetchRecentChats();
      } else {
        this.$router.push('/login');
        return;
      }
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Erro HTTP: ${response.status}`);
    }

    const data = await response.json();
    
    this.recentChats = Array.isArray(data) 
      ? data.map(chat => ({
          id: chat.id || Date.now().toString(),
          summary: chat.summary || "Sem mensagens ainda",
          timestamp: chat.timestamp || new Date().toISOString()
        }))
      : [];

  } catch (error) {
    console.error("Erro ao buscar histórico recente:", error);
    
    this.errorMessage = error.message || "Falha ao carregar histórico de chats";
    
    if (error.message.includes('401') || error.message.includes('autenticação')) {
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      this.$router.push('/login');
    }
    
    this.recentChats = [];
  }
},
async handleTokenRefresh() {
  try {
    const refreshToken = localStorage.getItem('refresh');
    if (!refreshToken) {
      return false;
    }

    const response = await fetch(`${baseURL}/chat/refresh/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ refresh: refreshToken })
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access', data.access);
      return true;
    }
    
    return false;
  } catch (error) {
    console.error("Erro ao renovar token:", error);
    return false;
  }
},
  },
  watch: {
    "$route.query.chatId": {
      immediate: true,
      handler() {
        this.fetchRecentChats();
      },
    },
  },
  mounted() {
    this.handleResize();
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
  },
};
</script>

<style scoped>

.chat-item {
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.sidebar-hidden {
  display: none !important;
}

.btn-close-mobile {
  background-color: transparent;
  border: none;
  font-size: 1.5rem;
  color: white;
}
.btn-close-mobile:hover {
  color: #ccc;
}

.chat-item:hover {
  background-color: #3b3b3b;
}

.sidebar {
  width: 250px;
  background-color: #000000;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: width 0.3s ease; 
  overflow-y: auto;
  height:100%;
}

.sidebar.collapsed {
  width: 50px; 
}

.sidebar .list-group {
  flex-grow: 1;
  width: 100%;
  padding: 0;
}

.sidebar .list-group-item  {
  background-color: transparent;
  border: none;
  color: #fff;
  text-align: center;
  transition: background-color 0.3s ease;
  border-radius:10px;
}

.sidebar .list-group-item:hover {
  background-color: #3b3b3b;
  border-radius:10px;
}


.sidebar .list-group-item .new-chat button {
  border:none;
}

.sidebar .list-group-item .new-chat {
  background-color: white;
  border: none;
  color: #fff;
  text-align: center;
  transition: background-color 0.3s ease;
}


.logout-item {
  margin-top: auto;
}

.toggle-btn {
  background-color: transparent;
  color: white;
  border: none;
  margin: 0.5rem;
  font-size: 22px;
  cursor: pointer;
  align-self: center; 
  transition: background-color 0.3s ease;
}

.toggle-btn:hover {
  background-color: #3b3b3b;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100%;
    width: 250px;
    z-index: 2000;
    transform: translateX(-100%);
    transition: transform 0.3s ease-in-out;
  }

  .sidebar.expanded-mobile {
    transform: translateX(0);
  }

  .toggle-btn {
    display: none;
  }
}
</style>