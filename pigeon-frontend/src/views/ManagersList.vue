<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Управляющие</h2>
      <button class="btn btn-primary" @click="showCreate = true">Добавить</button>
    </div>

    <table class="table">
      <thead><tr><th>ID</th><th>Логин</th><th>Действия</th></tr></thead>
      <tbody>
        <tr v-for="m in managers" :key="m.id">
          <td>{{ m.id }}</td>
          <td>{{ m.username }}</td>
          <td>
            <button class="btn btn-sm btn-outline-secondary me-1" @click="impersonate(m.id)">Войти</button>
            <button class="btn btn-sm btn-outline-danger">Удалить</button>
          </td>
        </tr>
      </tbody>
    </table>

    <BaseModal :visible="showCreate" title="Создать управляющего" @close="showCreate = false">
      <form @submit.prevent="createManager">
        <div class="mb-3">
          <input v-model="newManager.username" class="form-control" placeholder="Логин" required />
        </div>
        <div class="mb-3">
          <input v-model="newManager.password" type="password" class="form-control" placeholder="Пароль" required />
        </div>
        <button class="btn btn-primary" type="submit">Создать</button>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import api from '@/api/users'
import BaseModal from '@/components/BaseModal.vue'

const authStore = useAuthStore()
const router = useRouter()
const managers = ref([])
const showCreate = ref(false)
const newManager = ref({ username: '', password: '' })

onMounted(async () => {
  managers.value = await api.getManagers()
})

async function createManager() {
  await api.createManager(newManager.value)
  showCreate.value = false
  newManager.value = { username: '', password: '' }
  managers.value = await api.getManagers()
}

async function impersonate(id) {
  await authStore.impersonate(id)
  router.push('/manager/dashboard')
}
</script>