<template>
  <div class="chat-layout">
    <headerFuria @toggle-sidebar="toggleSidebarMobile" />

    <div class="d-flex">
      <sidebarFuria 
        :isMobileOpen="isMobileOpen" 
        @close-mobile="isMobileOpen = false"
      />

      <div class="chat-layout__content flex-grow-1">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import headerFuria from "@/components/headerFuria.vue";
import sidebarFuria from "@/components/sidebarFuria.vue";


export default {
  components: {
    headerFuria,
    sidebarFuria,
  },
  data(){
    return{
      isSidebarVisible: window.innerWidth > 768,
      isMobileOpen: false, 
    };
  },
  mounted() {
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
  },
  methods: {
    toggleSidebarMobile() {
      this.isMobileOpen = !this.isMobileOpen;
    },
    handleResize() {
      if (window.innerWidth > 768) {
        this.isSidebarVisible = true;
      }
    },
  },
};
</script>

<style>
.chat-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.chat-layout .d-flex {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-layout__content {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #787878 transparent;
}

.container::-webkit-scrollbar {
  width: 8px;
}

.container::-webkit-scrollbar-thumb {
  background-color: #787878;
  border-radius: 4px;
}

.container::-webkit-scrollbar-track {
  background-color: transparent;
}


</style>