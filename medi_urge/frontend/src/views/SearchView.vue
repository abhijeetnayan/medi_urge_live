<template>
  <div class="container-fluid h-100 p-0 overflow-hidden d-flex flex-column">
    
    <div class="bg-white border-bottom p-3 shadow-sm position-relative" style="z-index: 1050;">
      <div class="row g-2 align-items-center">
        
        <div class="col-md-3">
          <input v-model="searchQuery" type="text" class="form-control" placeholder="Search hospital name...">
        </div>
        
        <div class="col-md-2">
          <select v-model="typeFilter" class="form-select">
            <option value="">All Types</option>
            <option value="Government">Government</option>
            <option value="Private">Private</option>
          </select>
        </div>
        
        <div class="col-md-7 text-end">
          <button @click="useCurrentLocation" class="btn btn-primary btn-sm me-2 fw-bold">
            <i class="bi bi-geo-alt-fill"></i> Use My Location
          </button>
          
          <button data-bs-toggle="modal" data-bs-target="#applicationsModal" class="btn btn-info text-white btn-sm me-2 fw-bold">
            <i class="bi bi-card-list"></i> My Applications
          </button>
          
          <template v-if="!store.currentUser">
            <button data-bs-toggle="modal" data-bs-target="#loginModal" class="btn btn-outline-dark btn-sm me-2 fw-bold">
              Partner Login
            </button>
            <button data-bs-toggle="modal" data-bs-target="#registerModal" class="btn btn-success btn-sm fw-bold">
              Register Hospital
            </button>
          </template>
          <template v-else>
            <span class="me-3 text-warning fw-bold">Logged in as: {{ store.currentUser.role.toUpperCase() }}</span>
            <button @click="store.logout" class="btn btn-danger btn-sm fw-bold">Logout</button>
          </template>
        </div>

      </div>
    </div>

    <div class="row g-0 flex-grow-1">
      
      <div class="col-md-5 col-lg-4 bg-light border-end overflow-auto p-3 h-100" style="max-height: calc(100vh - 70px);">
        <p class="text-muted small mb-3">
          <i class="bi bi-info-circle"></i> Click on the map to set a custom location, or click a card to route.
        </p>
        
        <div v-if="filteredHospitals.length === 0" class="text-center text-muted mt-5">
          <p>No hospitals found matching your criteria.</p>
        </div>

        <div v-for="hosp in filteredHospitals" :key="hosp.id" 
             class="card mb-3 shadow-sm border-0" style="cursor:pointer;"
             @click="drawRouteToHospital(hosp)">
          <div class="card-body">
            
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="fw-bold mb-0 text-dark">{{ hosp.name }}</h5>
              <span :class="hosp.hosp_type === 'Government' ? 'bg-success' : 'bg-primary'" class="badge">
                {{ hosp.hosp_type }}
              </span>
            </div>
            
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span class="small fw-bold" :class="isUpdatedRecently(hosp.last_updated) ? 'text-success' : 'text-danger'">
                {{ isUpdatedRecently(hosp.last_updated) ? '● Updated (within 6h)' : '● Not Updated (6h+)' }}
              </span>
              <span class="badge bg-secondary">
                <i class="bi bi-signpost-split"></i> {{ hosp.distance?.toFixed(1) || '--' }} km
              </span>
            </div>

            <div class="row g-2 mb-3">
              <div v-for="res in hosp.resources" :key="res.type" class="col-6">
                <div class="border rounded p-2 text-center bg-white shadow-sm">
                  <span class="d-block small text-muted text-uppercase fw-bold" style="font-size: 0.65rem;">{{ res.type }}</span>
                  <span class="h5 fw-black mb-0 text-dark">{{ res.available }}</span>
                  <span class="d-block text-muted" style="font-size: 0.65rem;">
                    {{ res.price > 0 ? 'Rs.' + res.price : 'Free' }}
                  </span>
                </div>
              </div>
            </div>

            <button @click.stop="openTokenModal(hosp.id)" class="btn btn-dark w-100 fw-bold shadow-sm" data-bs-toggle="modal" data-bs-target="#tokenModal">
              Access Resources
            </button>
          </div>
        </div>
      </div>

      <div class="col-md-7 col-lg-8 position-relative bg-light h-100">
        <div id="map" class="h-100 w-100"></div>
        
        <div class="position-absolute bottom-0 end-0 m-4 p-3 bg-white border rounded-3 shadow-lg" style="z-index: 1000; min-width: 180px;">
          <h6 class="text-uppercase text-muted fw-bold mb-2" style="font-size: 0.7rem;">Legend (ICU Beds)</h6>
          <div class="d-flex align-items-center mb-1">
            <div class="rounded-circle bg-primary me-2" style="width: 12px; height: 12px;"></div>
            <span class="small fw-medium">Available (> 2)</span>
          </div>
          <div class="d-flex align-items-center">
            <div class="rounded-circle bg-danger me-2" style="width: 12px; height: 12px;"></div>
            <span class="small fw-medium">Critical (0-2)</span>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="tokenModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header bg-dark text-white border-0">
            <h5 class="modal-title fw-bold">Request Resource Access</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <p class="text-muted mb-4">Enter your mobile number. The hospital will contact you to confirm your arrival and secure the bed.</p>
            <input v-model="userMobile" type="tel" class="form-control form-control-lg mb-4 bg-light border-0" placeholder="e.g., 9876543210" maxlength="10">
            <button @click="submitRequest" class="btn btn-primary btn-lg w-100 fw-bold" data-bs-dismiss="modal">
              Generate Token
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="applicationsModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header bg-info text-white border-0">
            <h5 class="modal-title fw-bold">My Resource Applications</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4 bg-light">
            <div class="mb-4">
              <label class="form-label small fw-bold text-muted">Enter Mobile Number to Check Status</label>
              <div class="input-group">
                <input v-model="lookupMobile" type="tel" class="form-control" placeholder="10-digit mobile number">
                <button @click="loadMyApplications" class="btn btn-dark fw-bold">Check Status</button>
              </div>
            </div>

            <div v-if="hasSearched">
              <div v-if="store.myApplications.length === 0" class="text-center py-5 bg-white rounded shadow-sm border">
                <i class="bi bi-inbox fs-1 text-muted"></i>
                <h5 class="mt-3 text-muted">You have not yet applied for any resources.</h5>
              </div>

              <div v-else class="list-group shadow-sm">
                <div v-for="app in store.myApplications" :key="app.token" class="list-group-item p-3 border-0 mb-2 rounded bg-white shadow-sm">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <h5 class="fw-bold mb-1">{{ app.hospital }}</h5>
                      <p class="mb-0 small text-muted">
                        Token: <strong class="text-dark">{{ app.token }}</strong> | Applied: {{ new Date(app.timestamp).toLocaleTimeString() }}
                      </p>
                    </div>
                    <div class="text-end">
                      <span class="badge mb-2 d-block fs-6 shadow-sm" 
                            :class="{
                              'bg-warning text-dark': app.status === 'Pending',
                              'bg-success': app.status === 'Accepted',
                              'bg-danger': app.status === 'Denied',
                              'bg-secondary': app.status === 'Cancelled'
                            }">
                        {{ app.status }}
                      </span>
                      <button v-if="app.status === 'Pending'" @click="handleCancel(app.token)" class="btn btn-sm btn-outline-danger fw-bold w-100">
                        Cancel Request
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="loginModal" tabindex="-1">
      <div class="modal-dialog modal-sm modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header bg-primary text-white border-0">
            <h5 class="modal-title fw-bold">System Login</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" id="closeLoginModal"></button>
          </div>
          <div class="modal-body p-4">
            <input v-model="loginForm.username" type="text" class="form-control mb-3" placeholder="Username">
            <input v-model="loginForm.password" type="password" class="form-control mb-4" placeholder="Password">
            <button @click="handleLogin" class="btn btn-dark w-100 fw-bold">Log In</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="registerModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header bg-success text-white border-0">
            <h5 class="modal-title fw-bold">Register New Facility</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" id="closeRegisterModal"></button>
          </div>
          <div class="modal-body p-4">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label small fw-bold">Hospital Name</label>
                <input v-model="regForm.name" type="text" class="form-control">
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-bold">Type</label>
                <select v-model="regForm.hosp_type" class="form-select">
                  <option value="Private">Private</option>
                  <option value="Government">Government</option>
                </select>
              </div>
              <div class="col-12">
                <label class="form-label small fw-bold">Full Address</label>
                <input v-model="regForm.address" type="text" class="form-control">
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-bold">Latitude (e.g., 25.594)</label>
                <input v-model="regForm.latitude" type="number" step="0.0001" class="form-control">
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-bold">Longitude (e.g., 85.137)</label>
                <input v-model="regForm.longitude" type="number" step="0.0001" class="form-control">
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-bold text-primary">Login Username</label>
                <input v-model="regForm.username" type="text" class="form-control border-primary">
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-bold text-primary">Login Password</label>
                <input v-model="regForm.password" type="password" class="form-control border-primary">
              </div>
            </div>
            <button @click="handleRegistration" class="btn btn-success w-100 fw-bold mt-4">Submit for Verification</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useHospitalStore } from '../stores/hospitalStore'
import L from 'leaflet'

// 1. Core Setup
const router = useRouter()
const store = useHospitalStore()

// 2. Auth State
const loginForm = ref({ username: '', password: '' })
const regForm = ref({ name: '', address: '', latitude: null, longitude: null, hosp_type: 'Private', username: '', password: '' })

// 3. Map & Search State
const searchQuery = ref('')
const typeFilter = ref('')
const userMobile = ref('')
const selectedHospId = ref(null)

let map = null
let routingControl = null
let userMarker = null
let markers = []

// 4. Applications State
const lookupMobile = ref('')
const hasSearched = ref(false)


// LIFECYCLE HOOKS

onMounted(async () => {
  initMap()
  await store.fetchHospitals()
  window.addEventListener('open-token-modal', handlePopupClick)
})

onUnmounted(() => {
  window.removeEventListener('open-token-modal', handlePopupClick)
})


// AUTHENTICATION METHODS

const handleLogin = async () => {
  try {
    const user = await store.login(loginForm.value.username, loginForm.value.password)
    document.getElementById('closeLoginModal').click() 
    
    if (user.role === 'admin') {
      router.push('/admin')
    } else if (user.role === 'hospital') {
      router.push(`/hospital/${user.hospital_id}/dashboard`)
    }
  } catch (e) {
    alert(e.message) 
  }
}

const handleRegistration = async () => {
  if (!regForm.value.username || !regForm.value.password || !regForm.value.latitude) {
    return alert("Please fill all required fields.")
  }
  try {
    const res = await store.registerHospital(regForm.value)
    alert(res.message)
    document.getElementById('closeRegisterModal').click()
  } catch (e) {
    alert(e.message)
  }
}


// APPLICATIONS & CANCELLATION METHODS

const loadMyApplications = async () => {
  if (lookupMobile.value.length !== 10) {
    return alert("Please enter a valid 10-digit mobile number.")
  }
  await store.fetchMyApplications(lookupMobile.value)
  hasSearched.value = true
}

const handleCancel = async (token) => {
  if (confirm("Are you sure you want to cancel this request? You will lose your place in line.")) {
    try {
      await store.cancelApplication(token)
      alert("Request cancelled successfully.")
      await loadMyApplications() 
    } catch (e) {
      alert(e.message)
    }
  }
}


// MAP & ROUTING METHODS

const initMap = () => {
  map = L.map('map').setView([25.5941, 85.1376], 13)
  
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map)
  
  setTimeout(() => map.invalidateSize(), 200)

  map.on('click', (e) => {
    setOriginMarker(e.latlng.lat, e.latlng.lng, "Custom Location")
    store.userLocation = e.latlng
    store.fetchHospitals(e.latlng.lat, e.latlng.lng)
  })
}

const setOriginMarker = (lat, lng, popupText) => {
  if (userMarker) map.removeLayer(userMarker)
  const userIcon = L.divIcon({
    className: 'custom-user-icon',
    html: `<div style="background-color: #198754; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.5);"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  })
  userMarker = L.marker([lat, lng], { icon: userIcon }).addTo(map).bindPopup(`<b>${popupText}</b>`).openPopup()
  map.flyTo([lat, lng], 14)
}

const updateMapMarkers = () => {
  if (!map) return
  markers.forEach(m => map.removeLayer(m))
  markers = []

  filteredHospitals.value.forEach(hosp => {
    const icuResource = hosp.resources?.find(r => r.type === 'ICU Bed')
    const icuCount = icuResource ? icuResource.available : 0
    const markerColor = icuCount > 2 ? '#0d6efd' : '#dc3545'

    const marker = L.circleMarker([hosp.latitude, hosp.longitude], {
      radius: 9,
      fillColor: markerColor,
      color: '#ffffff',
      weight: 2,
      fillOpacity: 0.9
    }).addTo(map)

    const popupHTML = `
      <div class="text-center p-1" style="min-width: 160px;">
        <h6 class="fw-bold mb-1">${hosp.name}</h6>
        <span class="badge ${icuCount > 2 ? 'bg-primary' : 'bg-danger'} mb-2">ICU Beds: ${icuCount}</span>
        <br>
        <button class="btn btn-sm btn-dark w-100 fw-bold mt-1 shadow-sm" 
                onclick="window.dispatchEvent(new CustomEvent('open-token-modal', { detail: ${hosp.id} }))">
          Access Resources
        </button>
      </div>
    `
    marker.bindPopup(popupHTML)
    markers.push(marker)
  })
}

const drawRouteToHospital = (hosp) => {
  if (!store.userLocation) {
    alert("Please set your location on the map or click 'Use My Location' first.")
    return
  }
  if (routingControl) map.removeControl(routingControl)
  routingControl = L.Routing.control({
    waypoints: [
      L.latLng(store.userLocation.lat, store.userLocation.lng),
      L.latLng(hosp.latitude, hosp.longitude)
    ],
    routeWhileDragging: false,
    show: false, 
    createMarker: function() { return null; } 
  }).addTo(map)
}

const useCurrentLocation = () => {
  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition((pos) => {
      const lat = pos.coords.latitude
      const lng = pos.coords.longitude
      setOriginMarker(lat, lng, "You are here")
      store.userLocation = { lat, lng }
      store.fetchHospitals(lat, lng)
    }, (err) => {
      alert("Unable to retrieve your location.")
    })
  } else {
    alert("Geolocation is not supported by your browser.")
  }
}


// TOKEN METHODS

const isUpdatedRecently = (dateString) => {
  if (!dateString) return false
  const updatedDate = new Date(dateString)
  const sixHoursAgo = new Date(Date.now() - 6 * 60 * 60 * 1000)
  return updatedDate > sixHoursAgo
}

const handlePopupClick = (e) => {
  const hospitalId = e.detail
  openTokenModal(hospitalId)
  const modalElement = document.getElementById('tokenModal')
  if (modalElement) {
    // Note: If window.bootstrap error appears, ensure bootstrap JS CDN is in index.html
    new bootstrap.Modal(modalElement).show()
  }
}

const openTokenModal = (id) => {
  selectedHospId.value = id
}

const submitRequest = async () => {
  if (userMobile.value.length !== 10) {
    return alert("Please enter a valid 10-digit mobile number.")
  }
  try {
    const res = await store.requestResource(selectedHospId.value, userMobile.value)
    alert(`Success! Token: ${res.token}. The hospital will call you to confirm.`)
    userMobile.value = '' 
  } catch(e) {
    alert(e.response?.data?.error || "There was an error generating your token.")
  }
}


// COMPUTED & WATCHERS

const filteredHospitals = computed(() => {
  return store.hospitals.filter(h => {
    const nameMatch = h.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const typeMatch = typeFilter.value === "" || h.hosp_type === typeFilter.value
    return nameMatch && typeMatch
  })
})

watch(filteredHospitals, () => {
  if (map) updateMapMarkers()
}, { deep: true, immediate: true })

</script>

<style scoped>
.fw-black { font-weight: 900; }
.h-100 { height: 100vh !important; }
#map {
  min-height: calc(100vh - 70px);
  width: 100%;
}
</style>