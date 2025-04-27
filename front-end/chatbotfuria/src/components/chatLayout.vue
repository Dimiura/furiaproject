<template>
  <div class="chat-layout">
    <headerFuria />
    <div class="d-flex">
      <sidebarFuria />

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
}

.chat-layout__content {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
}
</style>