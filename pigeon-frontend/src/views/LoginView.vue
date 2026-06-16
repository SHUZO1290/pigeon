<template>
  <div class="container mt-5" style="max-width: 400px;">
    <h3 class="mb-4 text-center">Вход</h3>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <form @submit.prevent="login">
      <div class="mb-3">
        <label class="form-label">Логин</label>
        <input v-model="username" type="text" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Пароль</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>
      <button type="submit" class="btn btn-primary w-100">Войти</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()
const authStore = useAuthStore()

async function login() {
  try {
    error.value = ''
    await authStore.login(username.value, password.value)
    const role = authStore.user?.role
    if (role === 'owner') router.push('/owner/dashboard')
    else if (role === 'manager') router.push('/manager/dashboard')
    else if (role === 'cashier') router.push('/cashier/register')
  } catch (e) {
    error.value = 'Неверный логин или пароль'
  }
}
</script>