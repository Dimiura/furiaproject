import Login from "@/components/Login.vue";
import Register from "@/components/Register.vue";
import ChatLayout from "@/components/chatLayout.vue";
import chatBotAI from "@/components/chatBotAI.vue";
import { createRouter, createWebHistory } from "vue-router";

const routes = [
    { path: "/login", component: Login },
    { path: "/register", component: Register },
    {
      path: "/",
      component: ChatLayout,
      children: [
        { path: "", component: chatBotAI }, // Chatbot renderizado dentro do layout
      ],
    },
  ];

const router = createRouter({
    history: createWebHistory(),
    routes,
  });
  
  export default router;