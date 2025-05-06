<template>
     <div v-if="showModal" class="modal-backdrop">
       <div class="modal-content-custom fan-card-modal">
         <div class="fan-card">
           <div class="fan-card-header">
             <img src="../assets/logo-furia-white.png" alt="FURIA" class="logo">
             <h3>Carteirinha de Torcedor</h3>
           </div>
           
           <div class="fan-card-body">
             <div class="fan-photo-container">
              <div v-if="!photoUrl" class="photo-placeholder" @click="triggerFileInput">
                <i class="bi bi-camera"></i>
                <span>Adicionar foto</span>
              </div>
              <div v-else class="photo-preview">
                <img :src="photoUrl" alt="Foto do torcedor" class="fan-photo" @click="triggerFileInput">
                <div class="photo-overlay" @click="triggerFileInput">
                  <i class="bi bi-arrow-repeat"></i>
                  <span>Alterar foto</span>
                </div>
              </div>
              <input 
                ref="fileInput"
                type="file" 
                id="fanPhoto" 
                accept="image/*" 
                @change="handlePhotoUpload"
                class="photo-input"
              >
            </div>
             
             <div class="fan-info">
               <div class="info-row">
                 <span class="label">Nome:</span>
                 <span class="value">{{ userData.full_name }}</span>
               </div>
               <div class="info-row">
                 <span class="label">RG:</span>
                 <span class="value">{{ userData.rg }}</span>
               </div>
               <div class="info-row">
                 <span class="label">CPF:</span>
                 <span class="value">{{ userData.cpf }}</span>
               </div>
               <div class="info-row">
                 <span class="label">Nível:</span>
                 <span class="value fan-level" :class="userData.fan_level">{{ fanLevelDisplay }}</span>
               </div>
             </div>
           </div>
           
           <div class="fan-card-footer">
             <small>Válida por 1 ano - Emitida em: {{ issueDate }}</small>
           </div>
         </div>
         
         <div class="modal-actions">
         <button class="btn btn-primary" @click="savePhoto" :disabled="uploading">
           <span v-if="uploading">
             <span class="spinner-border spinner-border-sm" role="status"></span>
             Salvando...
           </span>
           <span v-else>
             <i class="bi bi-save"></i> Salvar Carteirinha
           </span>
         </button>
         <button class="btn btn-download" @click="downloadCard">
           <i class="bi bi-download"></i> Baixar
         </button>
         <button class="btn btn-close" @click="closeModal">Fechar</button>
       </div>
     </div>
   </div>
 </template>
   
<script>
import html2canvas from 'html2canvas';

export default {
  props: {
    showModal: Boolean,
    userData: Object
  },
  data() {
    return {
      photoUrl: null,
      photoFile: null,
      uploading: false,
      issueDate: new Date().toLocaleDateString('pt-BR')
    };
  },
  computed: {
    fanLevelDisplay() {
      const levels = {
        'doido_por_furia': 'DOIDO POR FÚRIA!',
        'fanatico': 'FANÁTICO',
        'big_fan': 'Grande Fã',
        'regular_fan': 'Fã Casual',
        'not_fan': 'Iniciante'
      };
      return levels[this.userData.fan_level] || this.userData.fan_level;
    }
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    async handlePhotoUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.photoFile = file;
        this.photoUrl = URL.createObjectURL(file);
      }
    },
    async loadFanCardPhoto() {
      try {
        const response = await fetch(
          'http://localhost:8000/api/v1/quiz/fan-card/',
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access')}`
            }
          }
        );

        if (response.ok) {
          const data = await response.json();
          if (data.photo) {
            // Adiciona um timestamp para evitar cache do navegador
            this.photoUrl = `${data.photo}?${new Date().getTime()}`;
          }
        } else {
          console.error('Erro ao carregar foto:', await response.text());
        }
      } catch (error) {
        console.error('Erro na requisição:', error);
      }
    },
    async savePhoto() {
      if (!this.photoFile) {
        this.$toast.warning('Selecione uma foto primeiro');
        return;
      }

      this.uploading = true;
      
      try {
        const formData = new FormData();
        formData.append('photo', this.photoFile);

        const response = await fetch(
          'http://localhost:8000/api/v1/quiz/fan-card/',
          {
            method: 'PATCH',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access')}`
            },
            body: formData
          }
        );

        if (!response.ok) {
          throw new Error(await response.text());
        }

        // Recarrega a foto após salvar
        await this.loadFanCardPhoto();
        this.$toast.success('Foto atualizada com sucesso!');
      } catch (error) {
        console.error('Erro:', error);
        this.$toast.error(error.message || 'Erro ao salvar foto');
      } finally {
        this.uploading = false;
      }
    },
    downloadCard() {
      html2canvas(document.querySelector('.fan-card')).then(canvas => {
        const link = document.createElement('a');
        link.download = 'carteirinha-furia.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
      });
    },
    closeModal() {
      this.$emit('close');
    }
  },
  mounted() {
    this.loadFanCardPhoto();
  }
};
</script>
   
   <style scoped>
   .fan-card-modal {
     max-width: 600px;
     background: transparent;
     padding: 0;
   }
   
   .fan-card {
     background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
     border-radius: 15px;
     border: 2px solid white;
     overflow: hidden;
     box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
   }
   
   .fan-card-header {
     background-color: black;
     padding: 15px;
     text-align: center;
     font-weight: bold;
   }
   
   .fan-card-header .logo {
     height: 40px;
     margin-bottom: 10px;
   }
   
   .fan-card-body {
     display: flex;
     padding: 20px;
     gap: 20px;
   }
   
   .fan-photo-container {
     width: 150px;
     height: 180px;
     border: 2px dashed white;
     border-radius: 8px;
     display: flex;
     align-items: center;
     justify-content: center;
     position: relative;
     overflow: hidden;
   }
   
   .photo-placeholder {
     text-align: center;
     font-size: 14px;
   }
   
   .photo-placeholder i {
     font-size: 40px;
     display: block;
     margin-bottom: 10px;
   }
   
   .fan-photo {
     width: 100%;
     height: 100%;
     object-fit: cover;
   }
   
   .photo-input {
     position: absolute;
     width: 100%;
     height: 100%;
     opacity: 0;
     cursor: pointer;
   }
   
   .fan-info {
     flex: 1;
     display: flex;
     flex-direction: column;
     justify-content: center;
   }
   
   .info-row {
     margin-bottom: 15px;
     display: flex;
   }
   
   .label {
     font-weight: bold;
     width: 80px;
   }
   
   .value {
     flex: 1;
   }
   
   .fan-level.doido_por_furia {
     font-weight: bold;
     text-transform: uppercase;
   }
   
   .fan-level.fanatico {
     font-weight: bold;
   }
   
   .fan-card-footer {
     background-color: #1a1a1a;
     padding: 10px;
     text-align: center;
     font-size: 12px;
     color: #888;
   }
   
   .modal-actions {
     display: flex;
     justify-content: center;
     gap: 15px;
     margin-top: 20px;
   }
   
   .btn-download {
     background-color: black;
   }
   
   .btn-close {
     background-color: #333;
     color: white;
   }
   </style>