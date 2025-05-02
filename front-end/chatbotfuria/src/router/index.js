import Login from "@/components/Login.vue";
import Register from "@/components/Register.vue";
import ChatLayout from "@/components/chatLayout.vue";
import chatBotAI from "@/components/chatBotAI.vue";
import Quiz from "@/components/Quiz.vue"; // <-- Importa o novo componente
import { createRouter, createWebHistory } from "vue-router";
import TempPage from "@/components/TempPage.vue";

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
      { path: "quiz", component: Quiz, meta: { requiresAuth: true } }, 
    ],
    meta: { requiresAuth: true }
  },
  {
    path: '/terms',
    component: TempPage ,
    meta: { title: 'Termos de Serviço' }
  },
  {
    path: '/privacy',
    component:  TempPage,
    meta: { title: 'Política de Privacidade' }
  }
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