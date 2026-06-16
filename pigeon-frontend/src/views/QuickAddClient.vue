<template>
  <div class="p-3 border rounded bg-light">
    <h5>{{ editMode ? 'Редактирование' : 'Быстрое добавление' }}</h5>
    <form @submit.prevent="save">
      <div v-for="col in columns" :key="col.id" class="mb-2">
        <label class="form-label">{{ col.name }}</label>
        <input
          v-if="col.col_type !== 'select' && col.col_type !== 'date'"
          v-model="formData[col.name]"
          class="form-control"
          :type="col.col_type === 'number' ? 'number' : 'text'"
        />
        <input
          v-if="col.col_type === 'date'"
          v-model="formData[col.name]"
          class="form-control"
          type="date"
        />
        <select v-if="col.col_type === 'select'" v-model="formData[col.name]" class="form-select">
          <option v-for="opt in col.options" :key="opt" :value="opt">{{ opt }}</option>
        </select>
      </div>
      <div class="d-flex justify-content-between">
        <button class="btn btn-success" type="submit">Сохранить</button>
        <button type="button" class="btn btn-secondary" @click="$emit('close')">Отмена</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  columns: Array,
  initialData: Object,
  editMode: { type: Boolean, default: false },
  tableId: Number
})
const emit = defineEmits(['saved', 'close'])

const formData = ref({})

function initData() {
  const data = {}
  const source = props.editMode ? (props.initialData.data || props.initialData) : {}
  props.columns.forEach(col => {
    data[col.name] = source[col.name] || ''
  })
  formData.value = data
}
watch(() => props.columns, initData, { immediate: true })
watch(() => props.initialData, initData)

async function save() {
  try {
    if (props.editMode) {
      const rowId = props.initialData.id   // получаем ID переданной строки
      if (!rowId) throw new Error('rowId is missing')
      await api.updateRow(rowId, formData.value)
    } else {
      await api.createRow(props.tableId, formData.value)
    }
    emit('saved')
  } catch (e) {
    console.error(e)
  }
}

import api from '@/api/cashRegister'
</script>