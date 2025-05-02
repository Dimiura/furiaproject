<template>
  <div class="container py-2">
    <div class=" bg-transparent border-0 p-3 mb-3 ">
      <div class="card-body">
        <div class="d-flex align-items-center justify-content-start mb-4 gap-3">
          <h1 class="card-title text-center mb-0 p-0">Que tipo de fã você é?</h1>
        </div>

        <p class="text-start">
          Garanta sua carteirinha de torcedor 
          <img src="../assets/logo-furia-white.png" width="auto" height="20" />
          ao preencher o formulário
        </p>

        <div v-if="successMessage" class="alert alert-success">
          {{ successMessage }}
        </div>

        <div v-if="errorMessage" class="alert alert-danger">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="submitForm">
          <div class="mb-4">
            <div class="mb-3">
              <label for="fullName" class="form-label">Nome completo</label>
              <input v-model="form.fullName" type="text" class="form-control" id="fullName" placeholder="Seu nome completo" required />
            </div>

            <div class="mb-3">
              <label for="cpf" class="form-label">CPF</label>
              <input v-model="form.cpf" type="text" class="form-control" id="cpf" placeholder="000.000.000-00" required @input="applyCpfMask" />
            </div>

            <div class="mb-3">
              <label for="rg" class="form-label">RG</label>
              <input
                v-model="form.rg"
                type="text"
                class="form-control"
                id="rg"
                placeholder="00.000.000-0"
                required
                v-mask="'##.###.###-#'"
              />
            </div>

            <div class="mb-3">
              <label for="email" class="form-label">Email</label>
              <input v-model="form.email" type="email" class="form-control" id="email" placeholder="seu@email.com" required />
            </div>

            <div class="mb-3">
              <label class="form-label">Adquiriu algum produto da FURIA no último ano?</label>
              <div class="form-check">
                <input v-model="form.buy" class="form-check-input" type="radio" id="buyYes" value="yes" required />
                <label class="form-check-label" for="buyYes">Sim</label>
              </div>
              <div class="form-check">
                <input v-model="form.buy" class="form-check-input" type="radio" id="buyNo" value="no" />
                <label class="form-check-label" for="buyNo">Não</label>
              </div>

              <div v-if="form.buy === 'yes'" class="mt-3">
                <label for="buyDetails" class="form-label">Qual produto?</label>
                <input v-model="form.buyDetails" type="text" class="form-control" id="buyDetails" placeholder="Descreva o produto" />
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Esteve presente em algum evento da FURIA?</label>
              <div class="form-check">
                <input v-model="form.attendedEvent" class="form-check-input" type="radio" id="eventYes" value="yes" required />
                <label class="form-check-label" for="eventYes">Sim</label>
              </div>
              <div class="form-check">
                <input v-model="form.attendedEvent" class="form-check-input" type="radio" id="eventNo" value="no" />
                <label class="form-check-label" for="eventNo">Não</label>
              </div>

              <div v-if="form.attendedEvent === 'yes'" class="mt-3">
                <label for="eventCount" class="form-label">Quantos eventos?</label>
                <input v-model="form.eventCount" type="number" class="form-control" id="eventCount" placeholder="Digite o número de eventos" />
              </div>
            </div>

            <div class="mb-4">
              <h4>Conecte suas redes sociais para melhor experiência</h4>

              <!-- Botão de vincular Twitter -->
              <div class="mb-3">
                <button 
                  @click.prevent="linkTwitterAccount" 
                  class="btn btn-outline-primary d-flex align-items-center gap-2"
                  :disabled="isTwitterLinked"
                >
                  <i class="bi bi-twitter-x"></i>
                  {{ isTwitterLinked ? 'Conta do Twitter vinculada' : 'Vincular conta do Twitter' }}
                </button>
                <small v-if="isTwitterLinked" class="text-muted d-block mt-1">
                  Conta vinculada com sucesso!
                </small>
              </div>
            </div>

            <div class="mb-4">
              <label class="form-label d-flex align-items-center gap-2">
                Upload de Documento (para validação de identidade)
                <i class="bi bi-info-circle" @click="openModal" style="cursor: pointer;"></i>
              </label>

              <input
                ref="documentFile"
                type="file"
                class="form-control"
                id="document"
                multiple
                accept=".pdf,.jpg,.jpeg,.png"
                @change="validateFiles"
                required
              />
            </div>

            <div v-if="showModal" class="modal-backdrop">
              <div class="modal-content-custom">
                <h5 class="mb-3">Instruções para envio do documento</h5>
                <p>
                  Por favor, envie uma foto da <strong>frente e verso</strong> do seu RG ou CPF para validação de identidade.
                </p>
                <button class="btn mt-3" @click="closeModal">Entendi</button>
              </div>
            </div>

            <div class="mb-4">
              <div class="form-check">
                <input v-model="form.allowConversationHistory" class="form-check-input" type="checkbox" id="allowConversationHistory" />
                <label class="form-check-label" for="allowConversationHistory">
                  Você permite usar seu histórico de conversação com o FuriosoBOT para melhorar a experiência?
                </label>
              </div>
            </div>

            <div class="mb-5">
              <div class="form-check">
                <input v-model="form.acceptLgpd" class="form-check-input" type="checkbox" id="acceptLgpd" required />
                <label class="form-check-label" for="acceptLgpd">
                  Eu aceito os termos da LGPD e autorizo o uso dos meus dados.
                </label>
              </div>
            </div>

            <div class="d-grid">
              <button type="submit" class="btn" :disabled="loading">
                {{ loading ? 'Enviando...' : 'Enviar' }}
              </button>
            </div>

            <div class="loading-overlay" v-if="loading">
              <div class="loading-content">
                <div class="spinner"></div>
                <p>{{ statusMessage }}</p>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Quiz",
  data() {
    return {
      form: {
        statusMessage: '', 
        fullName: "",
        email: "",
        cpf: "",
        rg: "", 
        buy: "",
        buyDetails: "",
        attendedEvent: "",
        eventCount: "",
        selectedSocials: [],
        socialLinks: {},
        allowConversationHistory: false,
        acceptLgpd: false,
      },
      isTwitterLinked: false,
      twitterUsername: '',
      showModal: false,
      successMessage: '',
      errorMessage: '',
      loading: false
    };
  },
  methods: {
    async linkTwitterAccount() {
    this.statusMessage = "Preparando vinculação...";
    this.loading = true;
    this.successMessage = '';
    this.errorMessage = '';

    try {
        let accessToken = localStorage.getItem("access");
        
        const makeRequest = async () => {
            this.statusMessage = "Conectando com Twitter...";
            const headers = {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            };
            
            return await fetch('http://localhost:8000/api/v1/quiz/auth/twitter/start/', {
                headers: headers,
                credentials: 'include'
            });
        };

        let response = await makeRequest();

        if (response.status === 401) {
            this.statusMessage = "Atualizando sessão...";
            const refreshToken = localStorage.getItem("refresh");
            const refreshResponse = await fetch("http://localhost:8000/chat/refresh/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh: refreshToken }),
                credentials: 'include'
            });

            if (refreshResponse.ok) {
                const data = await refreshResponse.json();
                localStorage.setItem("access", data.access);
                accessToken = data.access;
                response = await makeRequest();
            } else {
                this.errorMessage = "Sessão expirada. Faça login novamente.";
                this.loading = false;
                return;
            }
        }

        const result = await response.json();
        console.log("Response from /start:", result);

        if (!response.ok) {
            throw new Error(result.error || "Erro ao iniciar vinculação");
        }

        this.statusMessage = "Abrindo Twitter...";
        
        const width = 600;
        const height = 700;
        const left = (window.screen.width - width) / 2;
        const top = (window.screen.height - height) / 2;
        
        const popup = window.open(
            result.auth_url,
            'twitter_auth',
            `width=${width},height=${height},left=${left},top=${top},scrollbars=yes,resizable=yes`
        );
        
        const checkPopup = setInterval(() => {
            if (popup.closed) {
                clearInterval(checkPopup);
                this.checkTwitterStatus().then(() => {
                    if (!this.isTwitterLinked) {
                        console.log("Vinculação falhou");
                    }
                });
            }
        }, 500);
        
    } catch (error) {
        console.error("Erro completo:", error);
        this.errorMessage = error.message || "Erro inesperado ao conectar com Twitter.";
    } finally {
        this.loading = false;
    }
},
    applyCpfMask(event) {
      let value = event.target.value.replace(/\D/g, '');
      if (value.length > 11) value = value.substring(0, 11);
      
      value = value.replace(/(\d{3})(\d)/, '$1.$2');
      value = value.replace(/(\d{3})(\d)/, '$1.$2');
      value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
      
      this.form.cpf = value;
    },
    validateFiles(event) {
        const documents = event.target.files;
          if (documents.length === 0) {
        this.errorMessage = "Você precisa enviar ao menos 1 documento.";
        event.target.value = "";
      } else {
        this.errorMessage = "";
      }
    },
    async submitForm() {
      console.log("[1] Iniciando envio do formulário");

      this.statusMessage = "Recebendo arquivos...";
      this.loading = true;

      this.successMessage = '';
      this.errorMessage = '';
      
      try {
        if (!this.form.acceptLgpd) {
          this.errorMessage = "Você deve aceitar os termos da LGPD";
          this.loading = false;
          return;
        }

        const fileInput = this.$refs.documentFile;
        if (!fileInput || fileInput.files.length === 0) {
        this.errorMessage = "Envie pelo menos 1 documento.";
        this.loading = false;
        return;
      }

        console.log("[2] Criando FormData");
        const formData = new FormData();
        
        formData.append('full_name', this.form.fullName);
        formData.append('email', this.form.email);
        formData.append('cpf', this.form.cpf.replace(/\D/g, ''));
        formData.append('rg', this.form.rg.replace(/\D/g, ''));
        formData.append('buy', this.form.buy);
        formData.append('buy_details', this.form.buyDetails || '');
        formData.append('attended_event', this.form.attendedEvent);
        formData.append('event_count', this.form.eventCount || '');
        formData.append('allow_conversation_history', this.form.allowConversationHistory);
        formData.append('accept_lgpd', this.form.acceptLgpd);

        this.form.selectedSocials.forEach(social => {
          formData.append(`social_links[${social}]`, this.form.socialLinks[social] || '');
        });

        for (let i = 0; i < fileInput.files.length; i++) {
          formData.append('documents', fileInput.files[i]);
        }

        console.log("[3] Preparando requisição");
        this.statusMessage = "Enviando dados para validação...";
        let accessToken = localStorage.getItem("access");
        
        const makeRequest = async () => {
          console.log("[4] Enviando para o backend");
          this.statusMessage = "Validando identificação...";
          const headers = {
            'Authorization': `Bearer ${accessToken}`
          };
          
          return await fetch('http://localhost:8000/api/v1/quiz/formulario/', {
            method: 'POST',
            body: formData,
            headers: headers
          });
        };

        console.log("[5] Fazendo requisição principal"); 
        let response = await makeRequest();
        console.log("[6] Resposta recebida:", response.status);

        if (response.status === 401) {
          console.log("[7] Tentando refresh token");
          this.statusMessage = "Atualizando sessão e revalidando...";
          const refreshToken = localStorage.getItem("refresh");
          const refreshResponse = await fetch("http://localhost:8000/chat/refresh/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh: refreshToken }),
          });

          if (refreshResponse.ok) {
            const data = await refreshResponse.json();
            localStorage.setItem("access", data.access);
            accessToken = data.access;

            response = await makeRequest();
          } else {
            this.errorMessage = "Sessão expirada. Faça login novamente.";
            this.loading = false;
            return;
          }
        }

        const result = await response.json();
        console.log("[8] Resultado completo:", result);
        this.statusMessage = "Concluído!";


        if (response.ok) {
          this.successMessage = "Documentos validados e recebidos com sucesso!";
          console.log("Resposta completa do servidor:", result);
          
          if (result.validation_result) {
            console.log("Detalhes da validação:", {
              valid: result.validation_result.valid,
              message: result.validation_result.message
            });
          }
          
          this.resetForm();
        } else {
          if (result.validation_details) {
            this.errorMessage = `Validação falhou: ${result.validation_details}`;
          } else {
            this.errorMessage = result?.error || "Erro ao enviar o formulário.";
          }
          
          console.error("Erro detalhado:", result);
        }
      } catch (error) {
        console.error("Erro completo:", error);
        this.errorMessage = error.message || "Erro inesperado. Tente novamente.";
      } finally {
        this.loading = false;
        console.log("[9] Processo finalizado"); 
      }
    },
    resetForm() {
      this.form = {
        fullName: "",
        email: "",
        cpf: "",
        rg: "", 
        buy: "",
        buyDetails: "",
        attendedEvent: "",
        eventCount: "",
        selectedSocials: [],
        socialLinks: {},
        allowConversationHistory: false,
        acceptLgpd: false,
      };
      if (this.$refs.documentFile) {
        this.$refs.documentFile.value = "";
      }
    },
    openModal() {
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },
    async checkTwitterStatus() {
    try {
      let accessToken = localStorage.getItem("access");
      
      const makeRequest = async () => {
        const headers = {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        };
        
        return await fetch('http://localhost:8000/api/v1/quiz/auth/twitter/status/', {
          headers: headers,
          credentials: 'include'
        });
      };

      let response = await makeRequest();

      if (response.status === 401) {
        console.log("[Twitter Status] Token expirado, tentando refresh...");
        const refreshToken = localStorage.getItem("refresh");
        const refreshResponse = await fetch("http://localhost:8000/chat/refresh/", {
          method: "POST",
          headers: { 
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh: refreshToken }),
          credentials: 'include'
        });

        if (refreshResponse.ok) {
          const data = await refreshResponse.json();
          localStorage.setItem("access", data.access);
          accessToken = data.access;
          console.log("[Twitter Status] Token atualizado, repetindo requisição...");
          
          response = await makeRequest();
        } else {
          console.log("[Twitter Status] Sessão expirada ao verificar status");
          this.errorMessage = "Sua sessão expirou. Por favor, faça login novamente.";
          return;
        }
      }

      const result = await response.json();

      if (response.ok) {
        console.log("[Twitter Status] Resposta OK:", result);
        this.isTwitterLinked = result.linked || false;
        this.twitterUsername = result.username || '';
        
        if (this.isTwitterLinked) {
          this.successMessage = `Conta @${this.twitterUsername} vinculada com sucesso!`;
        } else {
          this.errorMessage = result.error || "Falha ao verificar status do Twitter";
        }
      } else {
        console.error("[Twitter Status] Erro na resposta:", result);
        this.errorMessage = result.error || "Erro ao verificar status do Twitter";
      }
    } catch (error) {
      console.error("[Twitter Status] Erro completo:", error);
      this.errorMessage = "Erro inesperado ao verificar status";
    } finally {
      this.loading = false;
    }
  },
  },
  mounted() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('twitter_linked')) {
    this.isTwitterLinked = true;
    this.twitterUsername = urlParams.get('username');
    
    window.history.replaceState({}, document.title, window.location.pathname);
    
    this.successMessage = `Conta @${this.twitterUsername} vinculada com sucesso!`;
  }
  
  this.checkTwitterStatus();
}
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-content-custom {
  background-color: #000;
  color: #fff;
  border-radius: 12px;
  padding: 30px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0px 0px 20px rgba(255, 255, 255, 0.1);
  text-align: center;
}

.container {
  max-height: 100vh;
  padding-right: 15px;
}

input {
  background-color: #000;
  border: none;
  padding: 10px;
  color: #fff;
}

input:focus {
  outline: none;
  border: none;
  box-shadow: none;
  background-color: #000;
  color: #fff;
}

.btn {
  background-color: black;
  color: #fff;
  border: none;
  padding: 10px 20px;
  font-size: 1rem;
  font-weight: bold;
  text-transform: uppercase;
  transition: all 0.3s ease-in-out;
}

.btn:hover {
  background-color: #fff;
  color: #000;
  border-color: #000;
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn:disabled {
  opacity: 0.7;
  transform: none;
  box-shadow: none;
  background-color: #666;
}

.alert {
  padding: 12px;
  margin-bottom: 20px;
  border-radius: 6px;
  font-weight: bold;
}

.alert-success {
  background-color: #28a745;
  color: white;
}

.alert-danger {
  background-color: #dc3545;
  color: white;
}

.loading-overlay {
  position:absolute ;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #121212;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
  border-radius: 8px;
}

.loading-overlay .light-mode {

  background-color:#bababa;
}

.loading-content {
  text-align: center;
  color: #333;
  font-weight: bold;
  font-size: 1.2rem;
}

.spinner {
  border: 4px solid #ccc;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}



</style>