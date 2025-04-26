<template>
    <div>
      <h2>Registrar</h2>
      <form @submit.prevent="register">
        <input v-model="username" placeholder="Usuário" required />
        <input v-model="email" type="email" placeholder="Email" required />
        <input v-model="password" type="password" placeholder="Senha" required />
        <button type="submit">Registrar</button>
      </form>
      <p v-if="error">{{ error }}</p>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        username: "",
        email: "",
        password: "",
        error: null,
      };
    },
    methods: {
      async register() {
        try {
          const response = await fetch("http://localhost:8000/auth/register/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              username: this.username,
              email: this.email,
              password: this.password,
            }),
          });
          if (!response.ok) throw new Error("Registro falhou");
          this.$router.push("/login"); // Redirecionar após registro
        } catch (err) {
          this.error = "Erro ao registrar";
        }
      },
    },
  };
  </script>