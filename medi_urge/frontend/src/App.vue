<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm mb-4">
    <div class="container">
      <router-link class="navbar-brand fw-bold" to="/">Medi Urge</router-link>
      <div class="navbar-nav">
        <router-link class="nav-link" to="/">Find Resources</router-link>
        <router-link class="nav-link" to="/HospitalDashboard">About Developer</router-link>
      </div>
    </div>
  </nav>
  <main class="container">
    <router-view />
  </main>
</template>

<script setup>
import { onMounted } from 'vue'
import { useHospitalStore } from './stores/hospitalStore'

const store = useHospitalStore()

onMounted(() => {
  store.fetchHospitals()
})
</script>
