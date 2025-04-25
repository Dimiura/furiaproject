<template>
  <div class="chatbot-container">
    <div class="chatbot-container__wrapper">
      <div class="title-chat-window justify-content-center ">
        <div class="title">
          <p class="fs-4 text-light ">Posso te ajudar amigo? </p>
        </div>
      </div>
      <div class="chat-window">
        <div class="messages" ref="messagesContainer">
          <div v-for="(msg, i) in messages" :key="i" class="message-wrapper" :class="msg.role">
            <div v-if="msg.role === 'assistant'" class="avatar">
              <svg class="icon" version="1.0" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                viewBox="0 0 321.000000 312.000000" preserveAspectRatio="xMidYMid meet">

                <g transform="translate(0.000000,312.000000) scale(0.100000,-0.100000)" fill="#000" stroke="none">
                  <path d="M714 2988 c-16 -49 -7 -144 18 -199 53 -114 137 -169 273 -179 l90
              -6 -40 -18 c-39 -18 -107 -23 -190 -16 -79 7 -298 -122 -430 -255 -183 -183
              -305 -440 -322 -680 -3 -45 -2 -104 2 -131 l7 -49 13 35 c30 85 138 260 152
              246 2 -2 -12 -41 -30 -87 -66 -160 -82 -243 -82 -434 1 -145 4 -183 23 -255
              33 -122 101 -257 162 -322 46 -47 51 -50 46 -26 -14 62 -18 150 -11 213 4 36
              9 64 13 61 3 -3 15 -46 28 -94 75 -300 246 -508 501 -611 64 -26 162 -53 243
              -66 l35 -5 -25 17 c-56 41 -81 67 -119 125 -23 33 -41 65 -41 70 0 5 20 -7 43
              -26 58 -48 193 -110 292 -135 262 -65 509 -50 650 41 l50 32 -40 7 c-22 4 -66
              17 -97 29 -367 138 -488 621 -228 913 l49 54 -97 5 c-171 9 -303 70 -432 198
              -116 115 -181 269 -179 420 l1 55 13 -71 c41 -226 150 -378 340 -472 165 -82
              359 -91 545 -25 64 23 92 27 185 28 143 0 223 -24 338 -102 121 -83 194 -100
              289 -67 147 50 222 229 154 370 -13 27 -33 81 -45 119 -23 78 -57 139 -64 115
              -12 -39 -28 -171 -22 -180 3 -5 16 -10 28 -10 15 0 18 -3 10 -11 -6 -6 -21 -9
              -34 -7 -20 3 -25 12 -36 65 -7 35 -19 75 -27 90 -14 29 -54 69 -59 62 -2 -2
              -11 -40 -19 -84 -9 -44 -22 -94 -29 -112 l-14 -31 -90 24 c-49 13 -147 33
              -216 44 -70 11 -145 27 -168 36 -49 19 -81 56 -81 93 l0 26 19 -31 c24 -40 65
              -69 116 -83 64 -17 71 -13 28 18 -52 37 -67 76 -60 151 9 107 73 207 187 292
              l35 26 -45 -9 c-75 -16 -166 -66 -209 -116 -48 -54 -53 -46 -12 18 81 128 226
              177 448 149 55 -6 106 -15 113 -20 9 -6 11 -34 8 -109 -3 -71 0 -101 8 -101 6
              0 30 13 52 30 40 29 75 75 100 133 11 26 15 27 49 21 46 -8 55 -14 22 -14 -23
              0 -24 -3 -25 -75 -1 -53 3 -75 11 -75 23 0 82 77 100 129 9 28 20 51 24 51 14
              0 59 94 75 156 31 119 20 150 -73 218 -47 35 -88 83 -78 93 3 2 39 -14 79 -36
              41 -23 78 -41 81 -41 19 0 3 46 -25 71 -111 104 -355 199 -512 199 -86 0 -143
              12 -311 68 l-140 46 -145 0 c-137 0 -152 -2 -285 -38 -124 -34 -156 -39 -285
              -43 -169 -6 -295 13 -501 73 -173 51 -166 50 -175 22z m1321 -132 c40 -17 105
              -64 105 -77 0 -4 -4 -19 -10 -33 -8 -23 -12 -25 -37 -15 -15 6 -53 13 -83 17
              l-55 7 0 50 c0 46 -2 50 -23 48 -13 -2 -21 1 -17 7 9 15 81 12 120 -4z m234
              -102 c7 -6 -84 -44 -106 -44 -29 0 -29 8 -1 37 18 19 28 22 62 16 23 -3 43 -7
              45 -9z" />
                </g>
              </svg>
            </div>
            <div class="message" :class="msg.role">
              <strong>{{ msg.role === 'user' ? 'Você' : 'FURIOSO' }}: </strong>
              <span v-html="parseMarkdown(msg.content)"></span>
            </div>

            <div v-if="isTyping && msg.role === 'assistant'" class="typing-indicator">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>
        <form class="chat-input" @submit.prevent="sendMessage">
          <textarea ref="userInput" v-model="userInput" placeholder="Pergunte para o FuriosoBOT..." rows="1"
            @input="autoResize"></textarea>
          <button type="submit" class="icon-button"> Enviar
            <svg class="icon" version="1.0" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
              viewBox="0 0 321.000000 312.000000" preserveAspectRatio="xMidYMid meet">

              <g transform="translate(0.000000,312.000000) scale(0.100000,-0.100000)" fill="currentColor" stroke="none">
                <path d="M714 2988 c-16 -49 -7 -144 18 -199 53 -114 137 -169 273 -179 l90
            -6 -40 -18 c-39 -18 -107 -23 -190 -16 -79 7 -298 -122 -430 -255 -183 -183
            -305 -440 -322 -680 -3 -45 -2 -104 2 -131 l7 -49 13 35 c30 85 138 260 152
            246 2 -2 -12 -41 -30 -87 -66 -160 -82 -243 -82 -434 1 -145 4 -183 23 -255
            33 -122 101 -257 162 -322 46 -47 51 -50 46 -26 -14 62 -18 150 -11 213 4 36
            9 64 13 61 3 -3 15 -46 28 -94 75 -300 246 -508 501 -611 64 -26 162 -53 243
            -66 l35 -5 -25 17 c-56 41 -81 67 -119 125 -23 33 -41 65 -41 70 0 5 20 -7 43
            -26 58 -48 193 -110 292 -135 262 -65 509 -50 650 41 l50 32 -40 7 c-22 4 -66
            17 -97 29 -367 138 -488 621 -228 913 l49 54 -97 5 c-171 9 -303 70 -432 198
            -116 115 -181 269 -179 420 l1 55 13 -71 c41 -226 150 -378 340 -472 165 -82
            359 -91 545 -25 64 23 92 27 185 28 143 0 223 -24 338 -102 121 -83 194 -100
            289 -67 147 50 222 229 154 370 -13 27 -33 81 -45 119 -23 78 -57 139 -64 115
            -12 -39 -28 -171 -22 -180 3 -5 16 -10 28 -10 15 0 18 -3 10 -11 -6 -6 -21 -9
            -34 -7 -20 3 -25 12 -36 65 -7 35 -19 75 -27 90 -14 29 -54 69 -59 62 -2 -2
            -11 -40 -19 -84 -9 -44 -22 -94 -29 -112 l-14 -31 -90 24 c-49 13 -147 33
            -216 44 -70 11 -145 27 -168 36 -49 19 -81 56 -81 93 l0 26 19 -31 c24 -40 65
            -69 116 -83 64 -17 71 -13 28 18 -52 37 -67 76 -60 151 9 107 73 207 187 292
            l35 26 -45 -9 c-75 -16 -166 -66 -209 -116 -48 -54 -53 -46 -12 18 81 128 226
            177 448 149 55 -6 106 -15 113 -20 9 -6 11 -34 8 -109 -3 -71 0 -101 8 -101 6
            0 30 13 52 30 40 29 75 75 100 133 11 26 15 27 49 21 46 -8 55 -14 22 -14 -23
            0 -24 -3 -25 -75 -1 -53 3 -75 11 -75 23 0 82 77 100 129 9 28 20 51 24 51 14
            0 59 94 75 156 31 119 20 150 -73 218 -47 35 -88 83 -78 93 3 2 39 -14 79 -36
            41 -23 78 -41 81 -41 19 0 3 46 -25 71 -111 104 -355 199 -512 199 -86 0 -143
            12 -311 68 l-140 46 -145 0 c-137 0 -152 -2 -285 -38 -124 -34 -156 -39 -285
            -43 -169 -6 -295 13 -501 73 -173 51 -166 50 -175 22z m1321 -132 c40 -17 105
            -64 105 -77 0 -4 -4 -19 -10 -33 -8 -23 -12 -25 -37 -15 -15 6 -53 13 -83 17
            l-55 7 0 50 c0 46 -2 50 -23 48 -13 -2 -21 1 -17 7 9 15 81 12 120 -4z m234
            -102 c7 -6 -84 -44 -106 -44 -29 0 -29 8 -1 37 18 19 28 22 62 16 23 -3 43 -7
            45 -9z" />
              </g>
            </svg>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
  import {
    marked
  } from "marked";

  export default {
  data() {
    return {
      messages: [],
      userInput: "",
      isTyping: false, // Estado para controlar o "digitando"
      typingTimeout: null,
    };
  },
  methods: {
    sendMessage() {
      if (!this.userInput.trim()) return;

      const userMessage = { role: "user", content: this.userInput };
      this.messages.push(userMessage);
      const payload = {
        messages: [...this.messages],
      };
      this.userInput = "";

      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        container.scrollTop = container.scrollHeight;
      });

      fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
        .then((res) => res.json())
        .then((data) => {
          this.startTypingEffect(data.reply);
        })
        .catch((err) => {
          console.error("Erro ao enviar para o backend:", err);
          this.messages.push({
            role: "assistant",
            content: "Erro ao conectar com o FURIA bot. Tente novamente.",
          });
        });
    },
    
    // Simula o efeito de digitação
    startTypingEffect(message) {
      this.isTyping = true;
      
      // Aplica uma pequena pausa antes de adicionar a mensagem
      setTimeout(() => {
        this.isTyping = false;
        this.messages.push({ role: "assistant", content: message });
        this.$nextTick(() => {
          const container = this.$refs.messagesContainer;
          container.scrollTop = container.scrollHeight;
        });
      }, 2000); // Tempo para simular "digitando..." antes de mostrar a mensagem
    },
    
    parseMarkdown(text) {
      return marked(text);
    },
    mounted() {
      this.$nextTick(() => {
        this.$refs.userInput.focus();
      });
    },
  },
};
</script>

<style scoped>
  .chatbot-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem;
    overflow-y: auto;
  }

  .chatbot-container__wrapper {
    max-width: 700px;
    min-width: 600px;
    text-align: center;
    width: 100%;
  }

  .chat-window {
    background: #000000;
    width: 100%;
    max-width: 700px;
    display: flex;
    flex-direction: column;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    min-height: 100px;
    max-height: 80vh;
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
  }

  .message-wrapper {
    display: flex;
    align-items: flex-end;
    margin-bottom: 1rem;
    gap: 0.5rem;
  }

  .message-wrapper.user {
    justify-content: flex-end;
  }

  .message-wrapper.assistant {
    justify-content: flex-start;
  }

  .message.user {
    background-color: #080808;
    color: #fff;
    border-bottom-right-radius: 0;
  }

  .message.assistant {
    background-color: #080808;
    color: #fff;
    border-bottom-left-radius: 0;
  }

  .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
    margin-top: 5px;
    background-color: white;
    align-items: center;
    display: flex;
    justify-content: center;
  }

  .message {
    max-width: 75%;
    padding: 0.75rem;
    border-radius: 12px;
    word-wrap: break-word;
  }

  .chat-input {
    display: flex;
    gap: 0.5rem;
    padding: 1rem;
    background-color: #000000;
  }

  .chat-input textarea:focus {
    outline: none;
    border: none;
  }

  .chat-input textarea {
    flex: 1;
    resize: none;
    border: none;
    padding: 0.75rem;
    border-radius: 10px;
    background-color: #000000;
    color: #fff;
    font-size: 1rem;
    line-height: 1.5;
    max-height: 150px;
    overflow-y: auto;
  }

  .chat-input button {
    padding: 0.75rem 1rem;
    color: black;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    font-size: 14px;
    background-color: white;
    transition: color 0.7s;
  }

  .chat-input button:hover {
    background-color: black;
    color: white;
  } 

  .icon-button {
    background-color: transparent;
    border: none;
    padding: 0.75rem;
    border-radius: 8px;
    cursor: pointer;
  }

  .icon {
    color: black;
    transition: color 0.7s;
  }

  .icon-button:hover .icon {
    color: #fff;
  }

  .typing-indicator {
    display: flex;
    align-items: center;
    margin-top: 10px;
  }

  .typing-indicator .dot {
    width: 8px;
    height: 8px;
    margin-right: 5px;
    background-color: #fff;
    border-radius: 50%;
    animation: typing 1s infinite;
  }

  .typing-indicator .dot:nth-child(1) {
    animation-delay: 0s;
  }

  .typing-indicator .dot:nth-child(2) {
    animation-delay: 0.3s;
  }

  .typing-indicator .dot:nth-child(3) {
    animation-delay: 0.6s;
  }

  @keyframes typing {
    0% {
      opacity: 0;
    }

    50% {
      opacity: 1;
    }

    100% {
      opacity: 0;
    }
  }
</style>