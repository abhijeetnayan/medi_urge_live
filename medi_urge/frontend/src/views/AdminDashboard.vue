








<template>
  <div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
      <h1 class="display-6 fw-bold text-dark">Admin Control Center</h1>
      <router-link to="/" class="btn btn-outline-dark btn-sm">Back to Map</router-link>
    </div>

    <h4 class="fw-bold mb-3 text-danger">Pending Verifications</h4>
    <div class="card shadow-sm border-0">
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-dark">
            <tr>
              <th class="ps-4">Hospital Name</th>
              <th>Type</th>
              <th>Address</th>
              <th>Submitted Date</th>
              <th class="text-end pe-4">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="store.unverifiedHospitals.length === 0">
              <td colspan="5" class="text-center py-4 text-muted">No pending registrations.</td>
            </tr>
            <tr v-for="hosp in store.unverifiedHospitals" :key="hosp.id" class="align-middle">
              <td class="ps-4 fw-bold">{{ hosp.name }}</td>
              <td><span class="badge bg-secondary">{{ hosp.type }}</span></td>
              <td class="small">{{ hosp.address }}</td>
              <td class="small text-muted">{{ new Date(hosp.date).toLocaleDateString() }}</td>
              <td class="text-end pe-4">
                <button @click="verify(hosp.id)" class="btn btn-success btn-sm fw-bold shadow-sm">
                  <i class="bi bi-shield-check"></i> Verify & Go Live
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>



    <h4 class="fw-bold mb-3 mt-5 text-warning">Spam Reports & Moderation</h4>
<div class="card shadow-sm border-0">
  <div class="card-body p-0">
    <table class="table table-hover mb-0">
      <thead class="table-dark">
        <tr>
          <th class="ps-4">Reported Mobile</th>
          <th>Reason</th>
          <th>Date Reported</th>
          <th class="text-end pe-4">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="reports.length === 0">
          <td colspan="4" class="text-center py-4 text-muted">No pending user reports.</td>
        </tr>
        <tr v-for="rep in reports" :key="rep.id" class="align-middle">
          <td class="ps-4 fw-bold text-danger">{{ rep.mobile }}</td>
          <td>{{ rep.reason }}</td>
          <td class="small text-muted">{{ new Date(rep.date).toLocaleDateString() }}</td>
          <td class="text-end pe-4">
            <button @click="handleBan(rep.id)" class="btn btn-danger btn-sm fw-bold shadow-sm">
              <i class="bi bi-slash-circle"></i> Block Number
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>




  </div>
</template>

<script setup>
import {ref, onMounted } from 'vue'
import { useHospitalStore } from '../stores/hospitalStore'
import { useRouter } from 'vue-router'

const store = useHospitalStore()
const router = useRouter()

onMounted(() => {
  // Security check: bounce out if not admin
  if (store.currentUser?.role !== 'admin') {
    router.push('/')
    return
  }
  store.fetchUnverified()
})

const verify = async (id) => {
  if (confirm("Are you sure? This will make the hospital visible to the public.")) {
    await store.verifyHospital(id)
    // Refresh the public map data in the background
    store.fetchHospitals() 
  }
}




const reports = ref([])

onMounted(async () => {
  // ... your existing security check & fetchUnverified ...
  reports.value = await store.fetchUserReports()
})

const handleBan = async (reportId) => {
  if (confirm("Are you sure? This user will be permanently blocked from requesting resources.")) {
    await store.banUser(reportId)
    // Remove from UI
    reports.value = reports.value.filter(r => r.id !== reportId)
  }
}



</script>