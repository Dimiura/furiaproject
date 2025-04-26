<template>
    <div>
      <h2>Login</h2>
      <form @submit.prevent="login">
        <input v-model="username" placeholder="Usuário" required />
        <input v-model="password" type="password" placeholder="Senha" required />
        <button type="submit">Entrar</button>
      </form>
      <p v-if="error">{{ error }}</p>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        username: "",
        password: "",
        error: null,
      };
    },
    methods: {
      async login() {
        try {
          const response = await fetch("http://localhost:8000/auth/login/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: this.username, password: this.password }),
          });
          if (!response.ok) throw new Error("Login falhou");
          const data = await response.json();
          localStorage.setItem("access", data.access);
          localStorage.setItem("refresh", data.refresh);
          this.$router.push("/"); 
        } catch (err) {
          this.error = "Credenciais inválidas";
        }
      },
    },
  };
  </script>