<template>
  <div>
    <h3>Конструктор таблицы</h3>
    <div class="mb-3">
      <button class="btn btn-primary" @click="showAddCol = true">Добавить столбец</button>
    </div>
    <table class="table" v-if="table">
      <thead><tr><th>Название</th><th>Тип</th><th>Опции</th><th>Действия</th></tr></thead>
      <tbody>
        <tr v-for="col in table.columns" :key="col.id">
          <td>{{ col.name }}</td>
          <td>{{ col.col_type }}</td>
          <td>{{ col.options?.join(', ') }}</td>
          <td><button class="btn btn-sm btn-outline-danger" @click="deleteColumn(col.id)">Удалить</button></td>
        </tr>
      </tbody>
    </table>

    <BaseModal :visible="showAddCol" title="Новый столбец" @close="showAddCol = false">
      <form @submit.prevent="addColumn">
        <input v-model="newColumn.name" class="form-control mb-2" placeholder="Название" required />
        <select v-model="newColumn.col_type" class="form-select mb-2">
          <option value="text">Текст</option>
          <option value="number">Число</option>
          <option value="date">Дата</option>
          <option value="select">Выпадающий список</option>
        </select>
        <div v-if="newColumn.col_type === 'select'" class="mb-2">
          <input v-model="optionsStr" class="form-control" placeholder="Варианты через запятую" />
        </div>
        <button class="btn btn-primary" type="submit">Добавить</button>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/tables'
import BaseModal from '@/components/BaseModal.vue'

const route = useRoute()
const tableId = Number(route.params.tableId)
const table = ref(null)
const showAddCol = ref(false)
const newColumn = ref({ name: '', col_type: 'text' })
const optionsStr = ref('')

onMounted(async () => {
  table.value = await api.getTable(tableId)
})

async function addColumn() {
  let options = null
  if (newColumn.value.col_type === 'select') {
    options = optionsStr.value.split(',').map(s => s.trim())
    if (options.length === 0) options = null
  }
  await api.addColumn(tableId, {
    name: newColumn.value.name,
    col_type: newColumn.value.col_type,
    options
  })
  showAddCol.value = false
  newColumn.value = { name: '', col_type: 'text' }
  optionsStr.value = ''
  table.value = await api.getTable(tableId)
}

async function deleteColumn(columnId) {
  await api.deleteColumn(columnId)
  table.value = await api.getTable(tableId)
}
</script>