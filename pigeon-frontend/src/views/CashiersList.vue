<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Кассиры</h2>
      <button class="btn btn-primary" @click="showCreate = true">Добавить</button>
    </div>
    <table class="table">
      <thead><tr><th>ID</th><th>Логин</th><th>Действия</th></tr></thead>
      <tbody>
        <tr v-for="c in cashiers" :key="c.id">
          <td>{{ c.id }}</td>
          <td>{{ c.username }}</td>
          <td>
            <button class="btn btn-sm btn-outline-secondary me-1" @click="impersonate(c.id)">Войти</button>
            <button class="btn btn-sm btn-danger" @click="deleteCashier(c.id)">Удалить</button>
          </td>
        </tr>
      </tbody>
    </table>

    <BaseModal :visible="showCreate" title="Создать кассира" @close="showCreate = false">
      <form @submit.prevent="createCashier">
        <input v-model="newCashier.username" class="form-control mb-2" placeholder="Логин" required />
        <input v-model="newCashier.password" type="password" class="form-control mb-2" placeholder="Пароль" required />
        <button class="btn btn-primary" type="submit">Создать</button>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/users'
import BaseModal from '@/components/BaseModal.vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const auth = useAuthStore()
const cashiers = ref([])
const showCreate = ref(false)
const newCashier = ref({ username: '', password: '' })

onMounted(async () => {
  cashiers.value = await api.getCashiers()
})

async function createCashier() {
  await api.createCashier(newCashier.value)
  showCreate.value = false
  newCashier.value = { username: '', password: '' }
  cashiers.value = await api.getCashiers()
}

async function deleteCashier(id) {
  await api.deleteCashier(id)
  cashiers.value = await api.getCashiers()
}

async function impersonate(id) {
  await auth.impersonateCashier(id)
  router.push('/cashier/register')
}

</script>