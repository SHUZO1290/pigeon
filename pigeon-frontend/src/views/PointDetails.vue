<template>
  <div>
    <h3>Точка: {{ point?.name }}</h3>
    <div class="mb-3">
      <button class="btn btn-primary me-2" @click="showAddTable = true">Добавить таблицу</button>
      <button class="btn btn-secondary" @click="showAssignCashier = true">Привязать кассира</button>
    </div>

    <h4>Таблицы</h4>
    <ul class="list-group">
      <li v-for="table in point?.tables" :key="table.id" class="list-group-item d-flex justify-content-between align-items-center">
        {{ table.name }}
        <div>
          <button class="btn btn-sm btn-outline-primary me-1" @click="$router.push(`/manager/tables/${table.id}/builder`)">
            Редактировать
          </button>
          <button class="btn btn-sm btn-outline-danger" @click="deleteTable(table.id)">
            Удалить
          </button>
        </div>
      </li>
    </ul>

    <BaseModal :visible="showAddTable" title="Новая таблица" @close="showAddTable = false">
      <form @submit.prevent="addTable">
        <input v-model="newTableName" class="form-control mb-2" placeholder="Название таблицы" required />
        <button class="btn btn-primary" type="submit">Создать</button>
      </form>
    </BaseModal>

    <BaseModal :visible="showAssignCashier" title="Привязать кассира" @close="showAssignCashier = false">
      <select v-model="selectedCashierId" class="form-select mb-2">
        <option disabled value="">Выберите кассира</option>
        <option v-for="c in cashiers" :key="c.id" :value="c.id">{{ c.username }}</option>
      </select>
      <button class="btn btn-primary" @click="assignCashier">Привязать</button>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/points'
import tablesApi from '@/api/tables'
import BaseModal from '@/components/BaseModal.vue'

const route = useRoute()
const router = useRouter()
const pointId = Number(route.params.id)
const point = ref(null)
const cashiers = ref([])
const showAddTable = ref(false)
const showAssignCashier = ref(false)
const newTableName = ref('')
const selectedCashierId = ref('')

onMounted(async () => {
  point.value = await api.getPoint(pointId)
  cashiers.value = await api.getCashiers()
})

async function addTable() {
  await api.createTable(pointId, newTableName.value)
  showAddTable.value = false
  newTableName.value = ''
  point.value = await api.getPoint(pointId)
}

async function assignCashier() {
  if (selectedCashierId.value) {
    await api.assignCashier(pointId, selectedCashierId.value)
    showAssignCashier.value = false
    selectedCashierId.value = ''
    point.value = await api.getPoint(pointId)
  }
}

async function deleteTable(tableId) {
  if (!confirm('Удалить таблицу со всеми данными?')) return
  try {
    await tablesApi.deleteTable(tableId)
    point.value = await api.getPoint(pointId)
  } catch (e) {
    console.error(e)
    alert('Ошибка при удалении')
  }
}

function goToBuilder(tableId) {
  router.push(`/manager/tables/${tableId}/builder`)
}
</script>