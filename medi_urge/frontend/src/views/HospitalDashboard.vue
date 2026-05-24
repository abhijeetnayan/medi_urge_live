<template>
  <div class="container py-5">
    
    <div class="d-flex justify-content-between align-items-end mb-4 border-bottom pb-3">
      <div>
        <span class="badge bg-primary mb-2">Partner Facility Portal</span>
        <h1 class="display-6 fw-bold text-dark mb-0">{{ myData?.name || 'Loading...' }}</h1>
        <p class="text-muted mb-0"><i class="bi bi-geo-alt"></i> {{ myData?.address }}</p>
      </div>
      <div class="text-end">
        <button @click="loadDashboard" class="btn btn-outline-dark btn-sm fw-bold shadow-sm me-2">
          <i class="bi bi-arrow-clockwise"></i> Refresh Sync
        </button>
        <button @click="handleLogout" class="btn btn-danger btn-sm fw-bold shadow-sm">
          Logout
        </button>
      </div>
    </div>

    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="fw-bold mb-0">Live Inventory Management</h4>
      <button data-bs-toggle="modal" data-bs-target="#addResourceModal" class="btn btn-primary btn-sm fw-bold shadow-sm">
        + Add Custom Resource
      </button>
    </div>
    
    <div class="row g-4 mb-5">
      <div v-for="res in myData?.resources" :key="res.id" class="col-md-4">
        <div class="card shadow-sm border-0 h-100 position-relative">


          <button @click="removeResource(res.type)" class="btn btn-sm btn-outline-danger position-absolute top-0 end-0 m-2 border-0" title="Remove Resource Tracking">
            <i class="bi bi-x-lg"></i> Remove
          </button>


          <div class="card-body text-center p-4">
            <h6 class="text-uppercase text-muted fw-bold mb-3" style="font-size: 0.8rem; letter-spacing: 1px;">
              {{ res.type }}
            </h6>
            <h1 class="display-4 fw-black mb-0" :class="res.available <= 2 ? 'text-danger' : 'text-dark'">
              {{ res.available }}
            </h1>
            <p class="small text-muted mb-4">Price: {{ res.price > 0 ? 'Rs.' + res.price : 'Free' }}</p>
            
            <div class="d-flex justify-content-center gap-3 mt-auto">
              <button @click="updateResource(res.type, -1)" class="btn btn-outline-danger rounded-circle fw-bold d-flex align-items-center justify-content-center" style="width: 45px; height: 45px;">
                -
              </button>
              <button @click="updateResource(res.type, 1)" class="btn btn-outline-success rounded-circle fw-bold d-flex align-items-center justify-content-center" style="width: 45px; height: 45px;">
                +
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <h4 class="fw-bold mb-3 text-warning">Action Required: Pending Requests</h4>
    <div class="card shadow-sm border-0 mb-5 border-warning border-start border-4">
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th class="ps-4">Token ID</th>
              <th>Patient Mobile</th>
              <th>Time Requested</th>
              <th>Status</th>
              <th class="text-end pe-4">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="pendingRequests.length === 0">
              <td colspan="5" class="text-center py-4 text-muted">No pending requests in the queue.</td>
            </tr>
            <tr v-for="req in pendingRequests" :key="req.token" class="align-middle">
              <td class="ps-4"><span class="badge bg-light text-dark border fs-6">{{ req.token }}</span></td>
              <td class="fw-bold text-primary">{{ req.mobile }}</td>
              <td class="text-muted small">{{ new Date(req.timestamp).toLocaleTimeString() }}</td>
              <td><span class="badge bg-warning text-dark">Pending</span></td>
              <td class="text-end pe-4">
                <button @click="respondToToken(req.token, 'Accepted')" class="btn btn-success btn-sm fw-bold me-2 shadow-sm">
                  <i class="bi bi-check-lg"></i> Accept
                </button>
                <button @click="respondToToken(req.token, 'Denied')" class="btn btn-danger btn-sm fw-bold me-2 shadow-sm">
                  <i class="bi bi-x-lg"></i> Deny
                </button>
                <button @click="handleReport(req.mobile)" class="btn btn-outline-dark btn-sm fw-bold shadow-sm" title="Report Spam">
                  <i class="bi bi-flag-fill"></i> Report
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <h4 class="fw-bold mb-3 text-secondary">Application History Log</h4>
    <div class="card shadow-sm border-0 mb-5">
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-dark">
            <tr>
              <th class="ps-4">Token ID</th>
              <th>Patient Mobile</th>
              <th>Date & Time</th>
              <th>Final Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="requestHistory.length === 0">
              <td colspan="4" class="text-center py-4 text-muted">No historical data available.</td>
            </tr>
            <tr v-for="req in requestHistory" :key="req.token" class="align-middle">
              <td class="ps-4"><span class="badge bg-light text-dark border fs-6">{{ req.token }}</span></td>
              <td class="fw-bold">{{ req.mobile }}</td>
              <td class="text-muted small">
                {{ new Date(req.timestamp).toLocaleDateString() }} at {{ new Date(req.timestamp).toLocaleTimeString() }}
              </td>
              <td>
                <span class="badge fs-6 shadow-sm" 
                      :class="{
                        'bg-warning text-dark': req.status === 'Pending',
                        'bg-success': req.status === 'Accepted',
                        'bg-danger': req.status === 'Denied',
                        'bg-secondary': req.status === 'Cancelled'
                      }">
                  {{ req.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="modal fade" id="addResourceModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header bg-primary text-white border-0">
            <h5 class="modal-title fw-bold">Add New Resource Tracking</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" id="closeResModal"></button>
          </div>
          <div class="modal-body p-4">
            <input v-model="newResource.type" type="text" class="form-control mb-3" placeholder="Resource Name (e.g., Oxygen Cylinder)">
            <input v-model="newResource.available" type="number" class="form-control mb-3" placeholder="Initial Available Count">
            <input v-model="newResource.price" type="number" class="form-control mb-4" placeholder="Price per unit (Rs.)">
            <button @click="submitNewResource" class="btn btn-dark w-100 fw-bold">Add to Dashboard</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useHospitalStore } from '../stores/hospitalStore'
import { useRoute, useRouter } from 'vue-router'

const store = useHospitalStore()
const route = useRoute()
const router = useRouter()

const myData = ref(null)
const newResource = ref({ type: '', available: 0, price: 0 })

// Safely get the ID from the URL
const hospitalId = computed(() => route.params.id)

const loadDashboard = async () => {
  myData.value = await store.fetchHospitalDashboard(hospitalId.value)
}

onMounted(() => {
  // SECURITY CHECK
  if (!store.currentUser || store.currentUser.role !== 'hospital' || store.currentUser.hospital_id != hospitalId.value) {
    alert("Unauthorized access. Please log in.")
    router.push('/')
    return
  }
  loadDashboard()
})

// --- ACTIONS ---
const updateResource = async (type, change) => {
  await store.updateCount(hospitalId.value, type, change)
  loadDashboard() 
}

const respondToToken = async (token, decision) => {
  if (confirm(`Are you sure you want to ${decision.toUpperCase()} this request?`)) {
    await store.processTokenDecision(token, decision)
    loadDashboard() 
  }
}

const submitNewResource = async () => {
  if (!newResource.value.type) return alert("Type is required")
  try {
    await store.addCustomResource(hospitalId.value, newResource.value)
    document.getElementById('closeResModal').click()
    loadDashboard() 
    newResource.value = { type: '', available: 0, price: 0 } 
  } catch (e) {
    alert(e.message)
  }
}

const handleReport = async (mobile) => {
  if (confirm(`Report ${mobile} for spam? This sends their number to the Admin for blocking.`)) {
    await store.reportSpamUser(hospitalId.value, mobile)
  }
}

const handleLogout = () => {
  store.logout()
  router.push('/')
}








const removeResource = async (type) => {
  if (confirm(`Are you sure you want to permanently delete the tracking card for "${type}"?`)) {
    try {
      await store.deleteCustomResource(hospitalId.value, type)
      loadDashboard() // Instantly refresh the UI to make the card disappear
    } catch (e) {
      alert(e.message)
    }
  }
}




// --- COMPUTED PROPERTIES ---

// 1. Pending Queue (Requires Action)
const pendingRequests = computed(() => {
  if (!myData.value?.requests) return []
  return myData.value.requests.filter(r => r.status === 'Pending')
})

// 2. Full History (Sorted newest first)
const requestHistory = computed(() => {
  if (!myData.value?.requests) return []
  // Create a copy of the array and sort it by timestamp descending
  return [...myData.value.requests].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})
</script>

<style scoped>
.fw-black { font-weight: 900; }
</style>