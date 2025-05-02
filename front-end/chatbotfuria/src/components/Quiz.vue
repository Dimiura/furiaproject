
<template>
  <div class="container py-2">
    <div class="bg-transparent border-0 p-3 mb-3">
      <div class="card-body">
        <div class="d-flex align-items-center justify-content-start mb-4 gap-3">
          <h1 class="card-title text-center mb-0 p-0">Que tipo de fã você é?</h1>
        </div>

        <p class="text-start">
          Garanta sua carteirinha de torcedor 
          <img src="../assets/logo-furia-white.png" width="auto" height="20" />
        </p>

        
        <div v-if="hasExistingEntry === null" class="loading-overlay">
          <div class="loading-content">
            <div class="spinner"></div>
            <p>Verificando seu cadastro...</p>
          </div>
        </div>

        <form @submit.prevent="submitForm" v-else-if="!hasExistingEntry && !loadingCheck" >
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

              <div class="mb-3">
                <button 
                  @click.prevent="linkTwitterAccount" 
                  class="btn btn-outline-primary d-flex align-items-center gap-2"
                  :disabled="isTwitterLinked"
                >
                  <i class="bi bi-twitter-x"></i>
                  {{ isTwitterLinked ? 'Conta do Twitter vinculada' : 'Vincular conta do Twitter' }}
                </button>
               
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
           
          </div>
        </form>

        <div class="row" v-else-if="hasExistingEntry && currentEntry">
          <div class="col-md-6">
            <div class="card mb-4">
              <div class="card-header bg-dark text-white">
                <h5>Seu perfil atual</h5>
              </div>
              <div class="card-body">
                <div v-if="currentFanProfile">
                  <h6 class="text-muted">Nível de Torcedor:</h6>
                  <p class="h4" :class="fanLevelClass">
                    {{ currentEntry.fan_analysis.title }}
                  </p>
                  <p class="mb-3">{{ currentEntry.fan_analysis.description }}</p>
                  
                  <div class="mt-4">
                    <h6 class="text-muted">Detalhes:</h6>
                    <ul class="list-group list-group-flush">
                      <li class="list-group-item d-flex justify-content-between align-items-center">
                        Eventos FURIA
                        <span>{{ currentEntry.event_count || 0 }}</span>
                      </li>
                      <li class="list-group-item d-flex justify-content-between align-items-center">
                        Compras no último ano
                        <span>{{ currentEntry.buy === 'yes' ? 'Sim' : 'Não' }}</span>
                      </li>
                      <li class="list-group-item d-flex justify-content-between align-items-center">
                        Twitter vinculado
                        <span>{{ isTwitterLinked ? 'Sim' : 'Não' }}</span>
                      </li>
                      <li class="list-group-item d-flex justify-content-between align-items-center">
                        Mensagens no chat
                        <span>{{ chatMessageCount }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
                <div v-else>
                  <p>Carregando seu perfil...</p>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card mb-4">
              <div class="card-header bg-dark text-white">
                <h5>Atualizar perfil</h5>
              </div>
              <div class="card-body">
                <button 
                  @click="updateTwitterData"
                  class="btn btn-outline-primary mb-3 w-100"
                  :disabled="updatingTwitter"
                >
                  <span v-if="updatingTwitter">
                    <span class="spinner-border spinner-border-sm" role="status"></span>
                    Atualizando...
                  </span>
                  <span v-else>
                    <i class="bi bi-arrow-repeat"></i> Atualizar dados do Twitter
                  </span>
                </button>

                <div class="mb-3">
                  <label class="form-label">Atualizar número de eventos</label>
                  <input 
                    v-model="updateData.event_count" 
                    type="number" 
                    class="form-control" 
                    min="0"
                  >
                </div>

                <div class="mb-3">
                  <label class="form-label">Atualizar status de compras</label>
                  <select v-model="updateData.buy" class="form-select">
                    <option value="yes">Sim</option>
                    <option value="no">Não</option>
                  </select>
                </div>

                <div v-if="updateData.buy === 'yes'" class="mb-3">
                  <label class="form-label">Detalhes das compras</label>
                  <input 
                    v-model="updateData.buy_details" 
                    type="text" 
                    class="form-control"
                    placeholder="Quais produtos adquiriu?"
                  >
                </div>

                <div class="form-check mb-3">
                  <input 
                    v-model="updateData.allow_conversation_history" 
                    class="form-check-input" 
                    type="checkbox"
                    id="updateChatHistory"
                  >
                  <label class="form-check-label" for="updateChatHistory">
                    Usar meu histórico de chat para análise
                  </label>
                </div>

                <button 
                  @click="submitUpdate"
                  class="btn btn-primary w-100"
                  :disabled="updatingProfile"
                >
                  <span v-if="updatingProfile">
                    <span class="spinner-border spinner-border-sm" role="status"></span>
                    Atualizando...
                  </span>
                  <span v-else>
                    Atualizar Informações
                  </span>
                </button>
              </div>
            </div>
          </div>
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

            <div class="loading-overlay" v-if="loading">
              <div class="loading-content">
                <div class="spinner"></div>
                <p>{{ statusMessage }}</p>
              </div>
            </div>    
      </div>
      
    </div>
  </div>
</template>

<script>
  export default {
    name: "Quiz",
    data() {
      return {
        hasExistingEntry: null,
        currentEntry: null,
        currentFanProfile: null,
        loadingCheck: true,
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
      };
    },
    computed: {
      fanLevelDisplay() {
        if (!this.currentEntry) return '';
        const levels = {
          'hardcore_fan': 'Fanático',
          'super_fan': 'Super Fã',
          'regular_fan': 'Fã Regular',
          'casual_fan': 'Fã Casual',
          'not_fan': 'Iniciante'
        };
        return levels[this.currentEntry.fan_level] || this.currentEntry.fan_level;
      },
      fanLevelClass() {
        if (!this.currentEntry) return '';
        return this.currentEntry.fan_level || 'not_fan';
      }
    },
    methods: {

      async checkExistingEntry() {
        try {
          
          this.loadingCheck = true;
          this.errorMessage = '';
          
          this.loading = true;
          const response = await fetch('http://localhost:8000/api/v1/quiz/check-entry/', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access')}`
            },
            credentials: 'include'
          });

          if (response.status === 401) {
            await this.handleTokenRefresh();
            return this.checkExistingEntry(); 
          }

            const data = await response.json();
            this.hasExistingEntry = data.exists;
            if (data.exists) {
              this.currentEntry = data.entry;
              this.updateData = { 
                event_count: data.entry.event_count || 0,
                buy: data.entry.buy || 'no',
                buy_details: data.entry.buy_details || '',
                allow_conversation_history: data.entry.allow_conversation_history || false
              };
              await Promise.all([
                this.loadFanProfile(),
                this.loadChatHistory()
              ]);
            }
        } catch (error) {
          console.error("Erro ao verificar cadastro:", error);
          this.errorMessage = "Erro ao carregar perfil";
          this.hasExistingEntry = false
        } finally {
          this.loadingCheck = false;
        }
      },

      async handleTokenRefresh() {
        try {
          const refreshToken = localStorage.getItem("refresh");
          const response = await fetch("http://localhost:8000/chat/refresh/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh: refreshToken }),
            credentials: 'include'
          });

          if (response.ok) {
            const data = await response.json();
            localStorage.setItem("access", data.access);
            return true;
          }
          return false;
        } catch (error) {
          console.error("Erro ao atualizar token:", error);
          return false;
        }
      },

      async loadFanProfile() {

        try {
      let accessToken = localStorage.getItem("access");

          const response = await fetch('http://localhost:8000/api/v1/quiz/check-entry/', {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            },
            credentials: 'include'
          });

          if (response.ok) {
            this.currentFanProfile = await response.json();
          }
        } catch (error) {
          console.error("Erro ao carregar perfil:", error);
        }
      },

      async loadChatHistory() {
        try {
          let accessToken = localStorage.getItem("access");

            const response = await fetch('http://localhost:8000/chat/history-count/', {
              headers: {
                'Authorization': `Bearer ${accessToken}`
              },
              credentials: 'include'
            });

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

            if (response.ok) {
              const data = await response.json();
              this.chatMessageCount = data.user_message_count || 0;
            
            }
        } catch (error) {
          console.error("Erro ao carregar histórico:", error);
        }
      },

      async refreshTwitterValidation() {
          this.loading = true;
          this.statusMessage = "Atualizando dados do Twitter...";
          
          try {
            let accessToken = localStorage.getItem("access");
            const response = await fetch('http://localhost:8000/api/v1/quiz/refresh-validation/', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
              },
              credentials: 'include'
            });

            if (response.ok) {
              const data = await response.json();
              this.successMessage = `Perfil revalidado! Novo nível: ${data.new_level} (Score: ${data.new_score})`;
              
              if (data.twitter_data.follows_furia) {
                this.currentFanProfile.twitter.follows_furia = true;
              }
            } else {
              const error = await response.json();
              this.errorMessage = error.error || "Erro ao atualizar";
            }
          } catch (error) {
            this.errorMessage = "Erro de conexão";
          } finally {
            this.loading = false;
          }
        },

      async submitUpdate() {
        try {
          this.updatingProfile = true;
          let accessToken = localStorage.getItem("access");
          const response = await fetch('http://localhost:8000/api/v1/quiz/update-entry/', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.updateData),
            credentials: 'include'
          });

          if (response.ok) {
            this.successMessage = "Perfil atualizado com sucesso!";
            await this.checkExistingEntry(); 
          } else {
            const error = await response.json();
            this.errorMessage = error.message || "Erro ao atualizar";
          }
        } catch (error) {
          this.errorMessage = "Erro na conexão";
          console.error(error);
        } finally {
          this.updatingProfile = false;
        }
      },

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

      this.resetForm();
      this.checkExistingEntry();
      this.pollingInterval = setInterval(this.checkExistingEntry, 30000); 
      this.checkExistingEntry();

      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.has('twitter_linked')) {
        this.isTwitterLinked = true;
        this.twitterUsername = urlParams.get('username');
        
        window.history.replaceState({}, document.title, window.location.pathname);
        
        this.successMessage = `Conta @${this.twitterUsername} vinculada com sucesso!`;
      }
      
      this.checkTwitterStatus();
    },
    beforeDestroy() {
      clearInterval(this.pollingInterval);
    },
  };
  </script>

<style scoped>

.hardcore_fan {
  color: #dc3545;
  font-weight: bold;
}
.super_fan {
  color: #ffc107;
}
.regular_fan {
  color: #0d6efd;
}
.casual_fan {
  color: #0dcaf0;
}

.row {
  margin-top: 20px;
}

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