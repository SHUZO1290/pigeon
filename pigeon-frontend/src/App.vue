<template>
  <div id="app">
    <div v-if="authStore.user" class="d-flex">
      <Sidebar />
      <main class="flex-grow-1 p-3">
        <router-view />
      </main>
    </div>
    <div v-else>
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import Sidebar from '@/components/Sidebar.vue'

const authStore = useAuthStore()
</script>

<style>
</style>