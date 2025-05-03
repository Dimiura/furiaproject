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

       <p class="text-warning">{{ errorMessage }} </p> 

        
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
              <input v-model="form.full_name" type="text" class="form-control" id="fullName" placeholder="Seu nome completo" required />
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
                  required
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

        <div class="row"  v-else-if="hasExistingEntry && currentEntry">
          <div class="col-md-6">
            <div class=" mb-4">
              <div class="mb-2">
                <h5>Seu perfil atual</h5>
              </div>
              <div class="card-body">
                <div v-if="currentEntry">
                  <div class="d-flex gap-3 justify-content-start align-items-center">
                    <h6 class="">Nível de Torcedor:</h6>
                  <p class="h4" :class="currentEntry.fan_level">
                    {{ fanLevelDisplay }} 
                  </p>
                  </div>
                 
                  <p class="mb-3">{{ fanLevelDescription }}</p>
                  
                  <div class="mt-4">
                    <h6 class="">Detalhes:</h6>
                    <ul class="list-group-details p-3  rounded  ">
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

                    <div v-if="hasExistingEntry && currentEntry && isHighLevelFan" class="mt-4">
                      <button 
                        @click="showFanCardModal = true"
                        class="btn btn-primary w-100"
                      >
                        <i class="bi bi-card-text"></i> Minha Carteirinha de Torcedor
                      </button>
                    </div>
                  </div>
                </div>
                <div v-else>
                  <p>Carregando seu perfil...</p>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class=" mb-4">
              <div class=" ">
                <h5>Atualizar perfil</h5>
              </div>
              <div class="card-body">
                <button 
                  v-if="!isTwitterLinked"
                  @click="linkTwitterAccount"
                  class="btn btn-outline-primary mb-3 w-100"
                >
                  <i class="bi bi-twitter-x"></i> Vincular conta do Twitter
                </button>
                <button 
                  v-else
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
                  <label class="form-label">Comprou produtos FURIA no último ano?</label>
                  <select v-model="updateData.buy" class="form-select">
                    <option value="yes">Sim</option>
                    <option value="no">Não</option>
                  </select>
                </div>

                <div v-if="updateData.buy === 'yes'" class="mb-3">
                  <label class="form-label">Quantidade de compras</label>
                  <input 
                    v-model.number="updateData.buy_details" 
                    type="number" 
                    class="form-control"
                    min="0"
                    placeholder="Quantas compras você fez?"
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
          <div v-if="showFanCardModal">
          <Carteirinha 
            :showModal="showFanCardModal" 
            :userData="currentEntry"
            @close="showFanCardModal = false"
          />
        </div>
        </div>

       

        <div v-if="showModal" class="modal-backdrop">
              <div class="modal-content-custom">
                <h5 class="mb-3">Instruções para envio do documento</h5>
                <p>
                  Você pode enviar <strong>até</strong> 2 arquivos (.pdf, .jpg, .png, ...), desde que eles contenham a frente e o verso do documento.
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
  import Carteirinha from './Carteirinha.vue';

export default {
  components:{
    Carteirinha
  },
  name: "Quiz",
  data() {
    return {
      showFanCardModal: false,
      hasExistingEntry: null,
      currentEntry: null,
      loadingCheck: true,
      loading: false,
      updatingProfile: false,
      updatingTwitter: false,
      chatMessageCount: 0,
      form: {
        statusMessage: '',
        full_name: "",
        email: "",
        cpf: "",
        rg: "",
        buy: "",
        buyDetails: 0,
        attendedEvent: "",
        eventCount: 0,
        selectedSocials: [],
        socialLinks: {},
        allowConversationHistory: false,
        acceptLgpd: false,
      },
      updateData: {
        event_count: 0,
        buy: 'no',
        buy_details: 0,
        allow_conversation_history: false
      },
      isTwitterLinked: false,
      twitterUsername: '',
      showModal: false,
      successMessage: '',
      errorMessage: '',
    };
  },
  computed: {
    isHighLevelFan() {
      if (!this.currentEntry) return false;
      return ['fanatico', 'doido_por_furia'].includes(this.currentEntry.fan_level);
    },
    fanLevelDisplay() {
      const levels = {
        'doido_por_furia': 'DOIDO POR FÚRIA!',
        'fanatico': 'Fanático!!',
        'big_fan': 'Grande fã',
        'regular_fan': 'Fã Casual',
        'not_fan': 'Iniciante'
      };
      return this.currentEntry ? levels[this.currentEntry.fan_level] || this.currentEntry.fan_level : 'Você não é muito fã não né cara?';
    },
    fanLevelDescription() {
      const descriptions = {
        'doido_por_furia': 'COMPLETAMENTE MALUCO, LOUCO, SOLTA OS CACHORROS ART, UM AMANTE DE QUALQUER OBRA CRIADA PELA FÚRIA!! OBS: Cuide da saúde um pouco!!',
        'fanatico': 'Veste a camisa e torce como nunca, tem um pingo de loucura nisso você não acha? melhor eu perguntar para o gau se isso é saúdavel.',
        'big_fan': 'Você é um grande fã!, acompanha a FURIA mas pode se envolver mais!',
        'regular_fan': 'Você é um fã casual, está começando a acompanhar a FURIA.',
        'not_fan': 'Você está começando agora como fã da FURIA.'
      };
      return this.currentEntry ? descriptions[this.currentEntry.fan_level] || '' : '';
    },
    fanLevelClass() {
      return this.currentEntry ? this.currentEntry.fan_level || 'not_fan' : '';
    }
  },
  methods: {
    async checkExistingEntry() {
      try {
        this.loadingCheck = true;
        
        const response = await this.makeAuthenticatedRequest(
          'http://localhost:8000/api/v1/quiz/check-entry/'
        );

        const data = await response.json();
        console.log("Dados do chat recebidos:", data);
        this.hasExistingEntry = data.exists;
        
        if (data.exists) {
          this.currentEntry = {
            ...data.entry,
            fan_level: data.fan_level || 'not_fan',
            fan_score: data.fan_score || 0
          };
          
          this.updateData = { 
            event_count: data.entry.event_count || 0,
            buy: data.entry.buy || 'no',
            buy_details: data.entry.buy_details || '',
            allow_conversation_history: data.entry.allow_conversation_history || false
          };
          
          await this.loadChatHistory();
        }
      } catch (error) {
        this.handleError(error, "Erro ao carregar perfil");
        this.hasExistingEntry = false;
      } finally {
        this.loadingCheck = false;
      }
    },

    async handleTokenRefresh() {
      try {
        const refreshToken = localStorage.getItem("refresh");
        if (!refreshToken) {
          console.error("Nenhum refresh token disponível");
          return false;
        }

        const response = await fetch("http://localhost:8000/chat/refresh/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh: refreshToken }),
          credentials: 'include'
        });

        if (!response.ok) {
          localStorage.removeItem("access");
          localStorage.removeItem("refresh");
          return false;
        }

        const data = await response.json();
        localStorage.setItem("access", data.access);
        return true;
      } catch (error) {
        console.error("Erro ao atualizar token:", error);
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        return false;
      }
    },

    async makeAuthenticatedRequest(url, options = {}) {
      let accessToken = localStorage.getItem("access");
      
      const headers = {
        'Authorization': `Bearer ${accessToken}`,
        ...options.headers
      };

      let response = await fetch(url, { ...options, headers, credentials: 'include' });

      if (response.status === 401) {
        const refreshSuccess = await this.handleTokenRefresh();
        if (refreshSuccess) {
          accessToken = localStorage.getItem("access");
          headers.Authorization = `Bearer ${accessToken}`;
          response = await fetch(url, { ...options, headers, credentials: 'include' });
        } else {
          throw new Error("Sessão expirada. Faça login novamente.");
        }
      }

      return response;
    },

    async loadChatHistory() {
      try {
        const response = await this.makeAuthenticatedRequest(
          'http://localhost:8000/chat/history-count/'
        );

        if (response.ok) {
          const data = await response.json();
          console.log("Dados do chat recebidos:", data); 
          
          this.chatMessageCount = data.user_messages || 0;
          
        } else {
          console.error("Erro na resposta:", await response.json());
          this.chatMessageCount = 0;
        }
      } catch (error) {
        console.error("Erro ao carregar histórico:", error);
        this.chatMessageCount = 0;
      }
    },

    async submitForm() {
    try {
      this.loading = true;
      this.statusMessage = "Validando formulário...";
      this.errorMessage = '';

      const requiredFields = ['full_name', 'email', 'cpf', 'rg', 'buy', 'attendedEvent'];
      for (const field of requiredFields) {
        if (!this.form[field]) {
          this.errorMessage = `Preencha o campo ${field}`;
          this.loading = false;
          return;
        }
      }

      if (!this.form.acceptLgpd) {
        this.errorMessage = "Você deve aceitar os termos da LGPD";
        this.loading = false;
        return;
      }

      const files = this.$refs.documentFile?.files;
      if (!files || files.length === 0) {
        this.errorMessage = "Envie pelo menos 1 documento.";
        this.loading = false;
        return;
      }

      this.statusMessage = "Enviando dados...";
      
      const formData = new FormData();
      
      formData.append('full_name', this.form.full_name);
      formData.append('email', this.form.email);
      formData.append('cpf', this.form.cpf.replace(/\D/g, ''));
      formData.append('rg', this.form.rg.replace(/\D/g, ''));
      formData.append('buy', this.form.buy);
      formData.append('attended_event', this.form.attendedEvent);
      formData.append('accept_lgpd', 'true'); // Já validado acima
      
      formData.append('buy_details', this.form.buyDetails || '0');
      formData.append('event_count', this.form.eventCount || '0');
      formData.append('allow_conversation_history', this.form.allowConversationHistory.toString());

      for (let i = 0; i < files.length; i++) {
        formData.append('documents', files[i]);
      }

      for (let [key, value] of formData.entries()) {
        console.log(key, value);
      }

      const response = await this.makeAuthenticatedRequest(
        'http://localhost:8000/api/v1/quiz/formulario/', 
        {
          method: 'POST',
          body: formData
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || "Erro ao enviar formulário");
      }

      const result = await response.json();
      this.successMessage = "Cadastro realizado com sucesso!";
      this.hasExistingEntry = true;
      this.currentEntry = result.data;

    } catch (error) {
      console.error("Erro no submitForm:", error);
      this.errorMessage = error.message || "Erro ao processar o formulário";
      
      if (error.response) {
        console.error("Resposta do servidor:", await error.response.json());
      }
    } finally {
      this.loading = false;
      this.statusMessage = "";
    }
  },

    validateForm() {
      if (!this.form.acceptLgpd) {
        this.errorMessage = "Você deve aceitar os termos da LGPD";
        return false;
      }

      if (!this.$refs.documentFile || this.$refs.documentFile.files.length === 0) {
        this.errorMessage = "Envie pelo menos 1 documento.";
        return false;
      }

      return true;
    },

    prepareFormData() {
      const formData = new FormData();
      
      const fieldMapping = {
        'full_name': this.form.full_name,
        'email': this.form.email,
        'cpf': this.form.cpf.replace(/\D/g, ''),
        'rg': this.form.rg.replace(/\D/g, ''),
        'buy': this.form.buy,
        'buy_details': this.form.buyDetails || '0',
        'attended_event': this.form.attendedEvent,
        'event_count': this.form.eventCount || '0',
        'allow_conversation_history': this.form.allowConversationHistory ? 'true' : 'false',
        'accept_lgpd': this.form.acceptLgpd ? 'true' : 'false'
      };

    Object.entries(fieldMapping).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      formData.append(key, value);
    }
  });

      Array.from(this.$refs.documentFile.files).forEach(file => {
        formData.append('documents', file);
      });
      for (let [key, value] of formData.entries()) {
        console.log(key, value);
      }

      return formData;
    },

    handleFormResponse(result) {
      if (result.validation_result) {
        this.successMessage = "Documentos validados e recebidos com sucesso!";
        this.resetForm();
      } else {
        this.errorMessage = result.validation_details 
          ? `Validação falhou: ${result.validation_details}`
          : result?.error || "Erro ao enviar o formulário.";
      }
    },

    async submitUpdate() {
      try {
        this.updatingProfile = true;
        this.statusMessage = "Atualizando perfil...";

        const payload = {
          event_count: this.updateData.event_count,
          buy: this.updateData.buy,
          buy_details: this.updateData.buy === 'yes' ? this.updateData.buy_details : 0,
          allow_conversation_history: this.updateData.allow_conversation_history
        };

        console.log("Enviando payload:", payload); 

        const response = await this.makeAuthenticatedRequest(
          'http://localhost:8000/api/v1/quiz/update-entry/',
          {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          }
        );

        if (response.ok) {
          const updatedData = await response.json();
          this.currentEntry = {
            ...this.currentEntry,
            ...updatedData,
            buy_details: payload.buy_details,
            fan_level: updatedData.fan_level || this.currentEntry.fan_level,
            fan_score: updatedData.fan_score || this.currentEntry.fan_score
          };
          this.successMessage = `Perfil atualizado! Seu novo nível: ${this.fanLevelDisplay}`;
          
          this.$forceUpdate();
        } else {
          const error = await response.json();
          this.errorMessage = error.message || "Erro ao atualizar";
          console.error("Erro na resposta:", error);
        }
      } catch (error) {
        this.handleError(error, "Erro na conexão");
        console.error("Erro no submitUpdate:", error);
      } finally {
        this.updatingProfile = false;
        this.statusMessage = "";
      }
    },

    async updateTwitterData() {
      try {
        this.updatingTwitter = true;
        this.statusMessage = "Atualizando dados do Twitter...";
        
        const response = await this.makeAuthenticatedRequest(
          'http://localhost:8000/api/v1/quiz/refresh-validation/',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          }
        );

        if (response.ok) {
          const data = await response.json();
          this.currentEntry.fan_level = data.new_level;
          this.currentEntry.fan_score = data.new_score;
          
          this.successMessage = data.has_twitter_interaction 
            ? "Interação com a FURIA confirmada! Pontos adicionados." 
            : "Nenhuma interação recente com a FURIA encontrada.";
          
          this.$forceUpdate();
        } else {
          const error = await response.json();
          this.errorMessage = error.error || "Erro ao atualizar Twitter";
        }
      } catch (error) {
        console.error("Erro ao atualizar Twitter:", error);
        this.errorMessage = error.message || "Erro ao conectar com o Twitter";
      } finally {
        this.updatingTwitter = false;
        this.statusMessage = "";
      }
    },

    async linkTwitterAccount() {
      try {
        this.loading = true;
        this.statusMessage = "Preparando vinculação...";
        this.successMessage = '';
        this.errorMessage = '';

        const response = await this.makeAuthenticatedRequest(
          'http://localhost:8000/api/v1/quiz/auth/twitter/start/'
        );

        const result = await response.json();
        this.openTwitterAuthPopup(result.auth_url);
      } catch (error) {
        this.handleError(error, error.message || "Erro inesperado ao conectar com Twitter.");
      } finally {
        this.loading = false;
      }
    },

    openTwitterAuthPopup(url) {
      const width = 600;
      const height = 700;
      const left = (window.screen.width - width) / 2;
      const top = (window.screen.height - height) / 2;
      
      const popup = window.open(
        url,
        'twitter_auth',
        `width=${width},height=${height},left=${left},top=${top},scrollbars=yes,resizable=yes`
      );
      
      const checkPopup = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkPopup);
          this.checkTwitterStatus();
        }
      }, 500);
    },

    async checkTwitterStatus() {
      try {
        const response = await this.makeAuthenticatedRequest(
          'http://localhost:8000/api/v1/quiz/auth/twitter/status/'
        );

        const result = await response.json();
        this.isTwitterLinked = result.linked || false;
        this.twitterUsername = result.username || '';
        
        if (this.isTwitterLinked && this.currentEntry) {
          this.currentEntry.has_twitter = true;
        }
      } catch (error) {
        this.handleError(error, "Erro ao verificar status do Twitter");
      }
    },

    handleError(error, defaultMessage) {
      console.error(error);
      this.errorMessage = error.message || defaultMessage;
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
      if (event.target.files.length === 0) {
        this.errorMessage = "Você precisa enviar ao menos 1 documento.";
        event.target.value = "";
      } else {
        this.errorMessage = "";
      }
    },

    resetForm() {
      this.form = {
        full_name: "",
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
    }
  },
  mounted() {
    this.resetForm();
    this.checkExistingEntry();
    this.pollingInterval = setInterval(this.checkExistingEntry, 30000);

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
  }
};
</script>

<style scoped>

.list-group-details{
  display: flex;
  flex-direction: column;
  padding-left: 0;
  margin-bottom: 0;
  background-color: black;
}

.hardcore_fan {
  color: #dc3545;
  font-weight: bold;
}
.fanatico {
  color: #ffc107;
}
.big_fan {
  color: #0d6efd;
}
.regular_fan {
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