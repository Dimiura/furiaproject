<template>
  <div class="sidebar" :class="{ 'collapsed': !isExpanded }">
    <button class="toggle-btn btn btn-dark btn-sm " @click="toggleSidebar">
      <i :class="isExpanded ? 'bi bi-arrow-bar-left' : 'bi bi-arrow-bar-right'  "></i>
    </button>
    <ul class="list-group p-3" v-if="isExpanded">
   
      <li class="list-group-item logout-item mb-5 p-1">
        <button class="btn  w-100" @click="logout">Logout</button>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isExpanded: true, 
    };
  },
  methods: {
    toggleSidebar() {
      this.isExpanded = !this.isExpanded; 
    },
    logout() {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.sidebar {
  width: 250px;
  background-color: #000000;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: width 0.3s ease; 
  overflow: hidden;
}

.sidebar.collapsed {
  width: 50px; 
}

.sidebar .list-group {
  flex-grow: 1;
  width: 100%;
  padding: 0;
}

.sidebar .list-group-item {
  background-color: transparent;
  border: none;
  color: #fff;
  text-align: center;
  transition: background-color 0.3s ease;
}

.sidebar .list-group-item:hover {
  background-color: #3b3b3b;
}



.logout-item {
  margin-top: auto;
}

.toggle-btn {
  background-color: transparent;
  color: white;
  border: none;
  margin: 0.5rem;
  font-size: 22px;
  cursor: pointer;
  align-self: center; 
  transition: background-color 0.3s ease;
}

.toggle-btn:hover {
  background-color: #3b3b3b;
}
</style>