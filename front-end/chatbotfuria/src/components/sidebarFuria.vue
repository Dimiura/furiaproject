<template>
  <div class="sidebar" :class="{ 'collapsed': !isExpanded }">
    <button class="toggle-btn btn btn-dark btn-sm" @click="toggleSidebar">
      <i :class="isExpanded ? 'bi bi-arrow-bar-left' : 'bi bi-arrow-bar-right'"></i>
    </button>

    <ul class="list-group p-3" v-if="isExpanded">
  
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

export default {
  data() {
    return {
      isExpanded: true,
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
    openChat(chatId) {
      this.$router.push({ path: "/", query: { chatId } });
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
        const response = await fetch("http://localhost:8000/chat/recent-chats/", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        });
        if (!response.ok) {
          throw new Error("Erro ao buscar histórico recente");
        }
        const data = await response.json();
        this.recentChats = data.map(chat => ({
          id: chat.id,
          summary: chat.summary || "Sem mensagens ainda",
          timestamp: chat.timestamp
        }));
      } catch (error) {
        console.error("Erro ao buscar histórico recente:", error);
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
    this.fetchRecentChats();
  },
};
</script>

<style scoped>

.chat-item {
  cursor: pointer;
  transition: background-color 0.3s ease;
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
</style>