<template>
    <header class="headerFuria">
        <div class="container">
            <div class="container-fluid">
                <div class="d-flex justify-content-between text-center align-items-center">
                    <nav class="nav-link d-flex gap-3 align-items-center d-flex ">
                        <a href="https://www.furia.gg/" class="text-white text-decoration-none text-uppercase " target="_blank"><i>Site Furia</i></a>
                        <button class="theme-toggle" @click="toggleTheme" v-html="isDarkMode ? '<i class=\'bi bi-moon-fill\'></i>' : '<i class=\'bi bi-brightness-alt-high-fill\'></i>'">
                        </button>
                        <button class="btn btn-secondary"> Know your fan </button>
                    </nav>
                    <a href="https://www.furia.gg/" target="_blank"> 
                    <img src="../assets/logo-furia-white.png" alt="Logo da Furia" width="88" height="32"
                        fetchpriority="high"></a>

                </div>
            </div>
        </div>
    </header>
</template>




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


<script>
export default {
    data() {
        return {
            isDarkMode: false,
        };
    },
    methods: {
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