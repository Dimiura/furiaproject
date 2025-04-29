<template>
  <div class="container py-5">
    <div class="card bg-transparent text-white border-0 p-3 mb-5 ">
      <div class="card-body">
        <div class="d-flex align-items-center justify-content-start mb-4 gap-3">
          <h1 class="card-title text-center mb-0 p-0">Que tipo de fã você é?</h1>
        </div>

        <p class="text-start">
          Garanta sua carteirinha de torcedor 
          <img src="../assets/logo-furia-white.png" width="auto" height="20" />
          ao preencher o formulário
        </p>

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
                <input v-model="form.buy" class="form-check-input" type="radio" id="buyYes" value="yes" />
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
                <input v-model="form.attendedEvent" class="form-check-input" type="radio" id="eventYes" value="yes" />
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
              <h4>Redes Sociais</h4>

              <div v-for="(social, index) in socials" :key="index" class="form-check mb-2">
                <input class="form-check-input" type="checkbox" :id="social.value" v-model="form.selectedSocials" :value="social.value" />
                <label class="form-check-label" :for="social.value">
                  {{ social.label }}
                </label>

                <input
                  v-if="form.selectedSocials.includes(social.value)"
                  v-model="form.socialLinks[social.value]"
                  type="text"
                  class="form-control mt-2"
                  :placeholder="'Link do ' + social.label"
                />
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

            <div class="mb-4">
              <div class="form-check">
                <input v-model="form.acceptLgpd" class="form-check-input" type="checkbox" id="acceptLgpd" required />
                <label class="form-check-label" for="acceptLgpd">
                  Eu aceito os termos da LGPD e autorizo o uso dos meus dados.
                </label>
              </div>
            </div>

            <div class="d-grid">
              <button type="submit" class="btn">
                Enviar
              </button>
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
      socials: [
        { label: "LinkedIn", value: "linkedin" },
        { label: "Instagram", value: "instagram" },
        { label: "Facebook", value: "facebook" },
        { label: "Twitter (X)", value: "twitter" },
        { label: "Reddit", value: "reddit" }
      ],
      showModal: false,
    };
  },
  methods: {
    validateFiles(event) {
    const files = event.target.files;

    if (files.length > 2) {
      alert("Você pode enviar no máximo 2 arquivos.");
      event.target.value = ""; 
    }
  },
    async submitForm() {
      try {
        const formData = new FormData();

        formData.append('fullName', this.form.fullName);
        formData.append('email', this.form.email);
        formData.append('cpf', this.form.cpf);
        formData.append('buy', this.form.buy);
        formData.append('buyDetails', this.form.buyDetails);
        formData.append('attendedEvent', this.form.attendedEvent);
        formData.append('eventCount', this.form.eventCount);
        formData.append('allowConversationHistory', this.form.allowConversationHistory);
        formData.append('acceptLgpd', this.form.acceptLgpd);

        this.form.selectedSocials.forEach((social) => {
          formData.append(`socialLinks[${social}]`, this.form.socialLinks[social]);
        });

        const fileInput = this.$refs.documentFile;
      if (fileInput && fileInput.files.length > 0) {
        Array.from(fileInput.files).forEach((file) => {
          formData.append('documents', file); 
        });
      }
        const response = await fetch('http://localhost:8000/api/formulario/', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          alert('Formulário enviado com sucesso!');
        } else {
          alert('Erro ao enviar o formulário.');
        }
      } catch (error) {
        console.error(error);
        alert('Erro inesperado. Tente novamente.');
      }
    },
    openModal() {
    this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    }
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
  overflow-y: auto;
  padding-right: 15px;
  scrollbar-width: thin;
  scrollbar-color: #787878 transparent;
}

.container::-webkit-scrollbar {
  width: 8px;
}

.container::-webkit-scrollbar-thumb {
  background-color: #787878;
  border-radius: 4px;
}

.container::-webkit-scrollbar-track {
  background-color: transparent;
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
</style>
