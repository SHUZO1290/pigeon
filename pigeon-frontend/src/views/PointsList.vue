<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>{{ isOwner ? 'Все точки' : 'Мои точки' }}</h2>
      <button v-if="isOwner" class="btn btn-primary" @click="openCreateModal">
        Добавить точку
      </button>
    </div>

    <div v-if="points.length === 0" class="alert alert-info">
      Нет доступных точек.
    </div>

    <div class="row">
      <div class="col-md-4 mb-3" v-for="point in points" :key="point.id">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">{{ point.name }}</h5>
            <p class="card-text">{{ point.address || '—' }}</p>
            <p class="text-muted small">Управляющий ID: {{ point.manager_id }}</p>
            <button
              v-if="isManager"
              class="btn btn-outline-primary"
              @click="$router.push(`/manager/points/${point.id}`)"
            >
              Настроить
            </button>
          </div>
        </div>
      </div>
    </div>

    <BaseModal :visible="showCreate" title="Создать точку" @close="showCreate = false">
      <form @submit.prevent="createPoint">
        <div class="mb-3">
          <label class="form-label">Название</label>
          <input v-model="newPoint.name" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Адрес</label>
          <input v-model="newPoint.address" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Управляющий</label>
          <select v-model="newPoint.manager_id" class="form-select" required>
            <option disabled value="">Выберите управляющего</option>
            <option v-for="m in managers" :key="m.id" :value="m.id">
              {{ m.username }}
            </option>
          </select>
        </div>
        <button type="submit" class="btn btn-success">Создать</button>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import api from '@/api/points'
import apiUsers from '@/api/users'
import BaseModal from '@/components/BaseModal.vue'

const auth = useAuthStore()
const currentUser = computed(() => auth.user)
const isOwner = computed(() => currentUser.value?.role === 'owner')
const isManager = computed(() => currentUser.value?.role === 'manager')

const points = ref([])
const managers = ref([])
const showCreate = ref(false)
const newPoint = ref({ name: '', address: '', manager_id: '' })

onMounted(async () => {
  try {
    points.value = await api.getPoints()
    if (isOwner.value) {
      managers.value = await apiUsers.getManagers()
    }
  } catch (e) {
    console.error(e)
  }
})

function openCreateModal() {
  newPoint.value = { name: '', address: '', manager_id: '' }
  showCreate.value = true
}

async function createPoint() {
  if (!newPoint.value.name || !newPoint.value.manager_id) return
  await api.createPoint({
    name: newPoint.value.name,
    address: newPoint.value.address,
    manager_id: newPoint.value.manager_id,
  })
  showCreate.value = false
  points.value = await api.getPoints()
}
</script>