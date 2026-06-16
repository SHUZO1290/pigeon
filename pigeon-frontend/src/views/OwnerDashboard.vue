<template>
  <div>
    <h2>Главная</h2>
    <div class="row mt-4">
      <div class="col-md-3" v-for="card in cards" :key="card.title">
        <div class="card" :class="card.bg">
          <div class="card-body">
            <h5 class="card-title">{{ card.title }}</h5>
            <p class="card-text display-6">{{ card.value }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/dashboard'

const cards = ref([
  { title: 'Управляющих', value: 0},
  { title: 'Точек', value: 0},
  { title: 'Кассиров', value: 0},
  { title: 'Записей сегодня', value: 0}
])

onMounted(async () => {
  const data = await api.getOwnerDashboard()
  cards.value[0].value = data.total_managers
  cards.value[1].value = data.total_points
  cards.value[2].value = data.total_cashiers
  cards.value[3].value = data.rows_today
})
</script>