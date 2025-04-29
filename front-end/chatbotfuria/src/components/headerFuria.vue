<template>
    <header class="headerFuria">
        <div class="container">
            <div class="container-fluid">
                <div class="d-flex justify-content-between text-center align-items-center">
                    <nav class="nav-link d-flex gap-3 align-items-center d-flex ">
                        <a href="https://www.furia.gg/" class="text-white text-decoration-none text-uppercase " target="_blank"><i>Site Furia</i></a>
                        <button class="theme-toggle" @click="toggleTheme" v-html="isDarkMode ? '<i class=\'bi bi-moon-fill\'></i>' : '<i class=\'bi bi-brightness-alt-high-fill\'></i>'">
                        </button>
                        <button class="btn know-your-fan" @click="handleButtonClick">
                            {{ isQuizPage ? "ChatBot" : "Know your fan" }}
                            </button>
                    </nav>
                    <a href="https://www.furia.gg/" target="_blank"> 
                    <img src="../assets/logo-furia-white.png" alt="Logo da Furia" width="88" height="32"
                        fetchpriority="high"></a>
                </div>
            </div>
        </div>
    </header>
</template>

<script>
export default {
    data() {
        return {
            isDarkMode: false,
        };
    },
    computed: {
        isQuizPage() {
            return this.$route.path === "/quiz/"; 
        },
    },
    methods: {
        handleButtonClick() {
            if (this.isQuizPage) {
                this.$router.push("/"); 
            } else {
                this.$router.push("/quiz/"); 
            }
        },
        toggleTheme() {
            this.isDarkMode = !this.isDarkMode;
            document.body.classList.toggle('light-mode', this.isDarkMode);
        },
        async logout() {
            try {
                const refreshToken = localStorage.getItem("refresh");
                if (refreshToken) {
                    await fetch("http://localhost:8000/auth/logout/", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ refresh: refreshToken }),
                    });
                }
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");

                this.$router.push("/login");
            } catch (err) {
                console.error("Erro ao realizar logout:", err);
            }
        },
    },
};
</script>


<style>
    .headerFuria {
        height: 90px;
        background-color: #000000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 20px;
        color: white;
    }

    .theme-toggle {
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
    }

    .theme-toggle:hover {
        opacity: 0.8;
    }

    .know-your-fan {
        position: relative;
        background-color: transparent;
        color: white;
        border: none;
        padding: 10px 10px;
        font-size: 1rem;
        cursor: pointer;
        border-radius: 10px;
        overflow: hidden;
        z-index: 1;
    }

    .know-your-fan::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 0;
        height: 100%;
        background-color: white;
        z-index: -1;
        transition: width 0.3s ease-in-out;
    }

    .know-your-fan:hover::before {
        width: 100%;
    }

    .know-your-fan:hover {
        color: black; 
    }

    .nav-link {
        position: relative;
        color: white;
        text-decoration: none;
        font-size: 1rem;
    }

    .nav-link::after {
        content: '';
        position: absolute;
        left: 0;
        bottom: -2px;
        width: 0;
        height: 2px;
        background-color: white;
        transition: width 0.3s ease-in-out;
    }

  

    body {
        background-color: #121212;
        color: #ffffff;
    }

    body.light-mode {
        background-color: #f2f2f2;
        color: #000;
    }
</style>


