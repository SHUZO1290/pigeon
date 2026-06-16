<template>
  <table class="table table-bordered">
    <thead>
      <tr>
        <th v-for="col in columns" :key="col.id">{{ col.name }}</th>
        <th>Действия</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in rows" :key="row.id">
        <td v-for="col in columns" :key="col.id">
          {{ row.data[col.name] }}
        </td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" @click="$emit('edit', row)">Редактировать</button>
          <button class="btn btn-sm btn-outline-danger" @click="$emit('delete', row.id)">Удалить</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true }
})
defineEmits(['edit', 'delete'])
</script>