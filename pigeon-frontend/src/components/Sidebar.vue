<template>
  <nav class="bg-dark text-white p-3 d-flex flex-column" style="width: 220px; min-height: 100vh;">
    <div class="d-flex justify-content-center">
      <img src="/logo.svg" alt="logo" class="w-50">
    </div>
    <hr class="m-3">
    <ul class="nav d-flex flex-column flex-grow-1">
      <li v-if="authStore.user?.role === 'owner'">
        <router-link to="/owner/dashboard" class="nav-link text-white link-secondary">Главная</router-link>
        <router-link to="/owner/managers" class="nav-link text-white link-secondary">Управляющие</router-link>
        <router-link to="/owner/points" class="nav-link text-white link-secondary">Точки</router-link>
      </li>
      <li v-if="authStore.user?.role === 'manager'">
        <router-link to="/manager/dashboard" class="nav-link text-white link-secondary">Главная</router-link>
        <router-link to="/manager/cashiers" class="nav-link text-white link-secondary">Кассиры</router-link>
        <router-link to="/manager/points" class="nav-link text-white link-secondary">Точки</router-link>
      </li>
      <li v-if="authStore.user?.role === 'cashier'">
        <router-link to="/cashier/register" class="nav-link text-white link-secondary">Касса</router-link>
      </li>
      <li class="mt-auto">
        <button @click="authStore.logout()" class="btn btn-outline-light btn-sm w-100">Выйти</button>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
const authStore = useAuthStore()
</script>

<style scoped>
.nav-link.text-white:hover {
  color: var(--bs-secondary) !important;
}

.nav-link {
  transition: color 0.2s ease-in-out;
}

.router-link-active {
  color: var(--bs-secondary) !important;
}
</style>