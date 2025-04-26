<template>
    <div class="chat-layout">
      <headerFuria />
      <div class="chat-layout__content">
        <router-view />
      </div>
    </div>
  </template>
  
  <script setup>
  import headerFuria from './headerFuria.vue';
  </script>
  
  <style>
  .chat-layout {
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  .chat-layout__content {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow-y: auto;
    padding: 1rem;
  }
  </style>