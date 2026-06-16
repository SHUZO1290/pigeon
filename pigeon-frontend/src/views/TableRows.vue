<template>
  <div class="d-flex">
    <div class="flex-grow-1">
      <h3>{{ table?.name }}</h3>
      <DynamicTable
        v-if="table"
        :columns="table.columns"
        :rows="rows"
        @edit="startEdit"
        @delete="deleteRow"
      />
      <button class="btn btn-primary mt-2" @click="openQuickAdd">Добавить запись</button>
    </div>

    <div v-if="showQuickAdd" class="ms-3" style="width: 300px;">
      <QuickAddClient
        :columns="table?.columns"
        :table-id="tableId"
        @saved="onQuickAdd"
        @close="showQuickAdd = false"
      />
    </div>

    <BaseModal :visible="editModalVisible" title="Редактировать запись" @close="editModalVisible = false">
      <QuickAddClient
        v-if="editModalVisible"
        :columns="table?.columns"
        :table-id="tableId"
        :initialData="editRow"
        :editMode="true"
        @saved="onEditSaved"
        @close="editModalVisible = false"
      />
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/cashRegister'
import DynamicTable from '@/components/DynamicTable.vue'
import QuickAddClient from '@/views/QuickAddClient.vue'
import BaseModal from '@/components/BaseModal.vue'

const route = useRoute()
const tableId = Number(route.params.tableId)
const table = ref(null)
const rows = ref([])
const showQuickAdd = ref(false)
const editModalVisible = ref(false)
const editRow = ref(null)

onMounted(async () => {
  table.value = await api.getTable(tableId)
  rows.value = await api.getRows(tableId)
})

async function refreshRows() {
  rows.value = await api.getRows(tableId)
}

async function deleteRow(id) {
  await api.deleteRow(id)
  refreshRows()
}

function startEdit(row) {
  editRow.value = row
  editModalVisible.value = true
}

async function onEditSaved() {
  editModalVisible.value = false
  refreshRows()
}

async function onQuickAdd() {
  showQuickAdd.value = false
  refreshRows()
}

function openQuickAdd() {
  showQuickAdd.value = true
}
</script>