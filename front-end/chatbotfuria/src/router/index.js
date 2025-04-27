import Login from "@/components/Login.vue";
import Register from "@/components/Register.vue";
import ChatLayout from "@/components/chatLayout.vue";
import chatBotAI from "@/components/chatBotAI.vue";
import { createRouter, createWebHistory } from "vue-router";


function isAuthenticated() {
  return !!localStorage.getItem("access"); 
}

const routes = [
    { path: "/login", component: Login },
    { path: "/register", component: Register },
    {
      path: "/",
      component: ChatLayout,
      children: [
        { path: "", component: chatBotAI }, 
      ],
      meta: { requiresAuth: true }
    },
  ];

const router = createRouter({
    history: createWebHistory(),
    routes,
  });

  router.beforeEach((to, from, next) => {
    if (to.meta.requiresAuth && !isAuthenticated()) {
      next("/login"); 
    } else {
      next();
    }
  });
  
  export default router;