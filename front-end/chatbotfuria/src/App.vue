<template>
  <div class="app">
    <headerFuria />
    <div class="w-100 h-100 d-flex justify-content-center align-items-center">
      <div class="app__wrapper">
        <chatBotAI />
      </div>
    </div>

  </div>
</template>

<script setup>
import chatBotAI from './components/chatBotAI.vue'
import headerFuria from './components/headerFuria.vue'
</script>

<style>


.app {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.app__wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow-y: auto;
  padding: 1rem;
  height:100%;
}

headerFuria {
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 10;
}
</style>