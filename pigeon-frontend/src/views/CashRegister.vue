<template>
  <div>
    <h2>Касса</h2>
    <div class="list-group mt-3">
      <button
        v-for="table in tables"
        :key="table.id"
        class="list-group-item list-group-item-action"
        @click="$router.push(`/cashier/tables/${table.id}`)"
      >
        {{ table.name }} ({{ table.columns.length }} колонок)
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/cashRegister'

const tables = ref([])

onMounted(async () => {
  tables.value = await api.getTableList()
})
</script>