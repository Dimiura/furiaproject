<template>
  <div class="container">
    <div class="container-fluid d-flex justify-content-center align-items-center vh-100">
      <div class="row justify-content-center text-center w-100">
        <div class="col-6">
          <img class="img img-fluid ms-3" src="../assets/Furia_Esports_logo.svg" alt="Logo" />
        </div>
        <div class="col-6 d-flex text-center justify-content-center">
          <div class="register-card">
            <div class="title-register ">
              <h1> Register </h1>
            </div>
            <form @submit.prevent="register" class="form text-center">
              <input class="mt-3 input-form" v-model="username" placeholder="Usuário" required /> <br>
              <input class="mt-3 input-form" v-model="email" type="email" placeholder="Email" required /><br>
              <input class="mt-3 mb-3 input-form" v-model="password" type="password" placeholder="Senha" required /><br>
              <button class="btn btn-secondary" type="submit">Registrar</button> <br>
              <p class="mt-3">
                Já tem uma conta? <router-link to="/login">Entrar</router-link>
              </p>
            </form>
            <p v-if="error">{{ error }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
    .input-form {
      flex: 1;
      resize: none;
      border: none;
      padding: 0.75rem 3rem 0.75rem 0.75rem; 
      border-radius: 10px;
      background-color: #000000;
      color: #fff;
      font-size: 1rem;
      line-height: 1.5;
      max-height: 150px;
      overflow-y: auto;
      width:100%;
    }
  </style>

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
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              username: this.username,
              email: this.email,
              password: this.password,
            }),
          });
          if (!response.ok) throw new Error("Registro falhou");
          this.$router.push("/login"); 
        } catch (err) {
          this.error = "Erro ao registrar";
        }
      },
    },
  };
</script>