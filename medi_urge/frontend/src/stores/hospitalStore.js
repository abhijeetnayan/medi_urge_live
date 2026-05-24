import { defineStore } from 'pinia'
import axios from 'axios'


// In production, this pulls our Render URL. Locally, it defaults to our Flask port.
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'
axios.defaults.baseURL = API_URL





export const useHospitalStore = defineStore('hospitals', {
  state: () => ({
    hospitals: [],
    myApplications: [],
    loading: false,
    userLocation: null,



    // NEW: Auth State
    currentUser: null, // { role: 'admin' | 'hospital', id?: number, name?: string }
    unverifiedHospitals: []

    
  }),
  actions: {
    // async fetchHospitals() {
    //   this.loading = true
    //   try {
    //     const res = await axios.get('/api/hospitals')
    //     this.hospitals = res.data
    //   } catch (err) {
    //     console.error("Error fetching data", err)
    //   } finally {
    //     this.loading = false
    //   }

    async fetchHospitals(lat = null, lng = null) {
      this.loading = true
      try {
        let url = '/api/hospitals'
        if (lat && lng) url += `?lat=${lat}&lng=${lng}`
        const res = await axios.get(url)
        this.hospitals = res.data
      } catch (err) {
        console.error("Error fetching data", err)
      } finally {
        this.loading = false
      }

    },





    async requestResource(hospitalId, mobile) {
      try {
        const res = await axios.post('/api/request-token', { hospital_id: hospitalId, mobile })
        return res.data
      } catch (err) {
        throw new Error("Failed to request resource")
      }
    },




    async fetchMyApplications(mobile) {
      try {
        const res = await axios.get(`/api/my-applications?mobile=${mobile}`)
        this.myApplications = res.data
      } catch (err) {
        console.error(err)
      }

    } , 

    async updateCount(hospitalId, type, change) {
      try {
        const res = await axios.post(`/api/hospitals/${hospitalId}/update`, {
          type,
          change
        })
        const hosp = this.hospitals.find(h => h.id === hospitalId)
        if (hosp) {
          hosp.resources[type] = res.data.new_count
        }
      } catch (err) {
        alert("Failed to update resource")
      }
    },






    // Add inside your Pinia actions:

    async fetchHospitalDashboard(hospitalId) {
      try {
        const res = await axios.get(`/api/hospital/${hospitalId}/dashboard`)
        return res.data
      } catch (err) {
        console.error("Error fetching dashboard", err)
        return null
      }
    },

    async processTokenDecision(token, decision) {
      try {
        await axios.post('/api/hospital/token-decision', { token, decision })
        alert(`Token ${decision} successfully.`)
      } catch (err) {
        alert("Failed to process token.")
      }
    },












    // --- AUTHENTICATION ---
    async login(username, password) {
      try {
        const res = await axios.post('/api/login', { username, password })
        this.currentUser = res.data
        return res.data
      } catch (err) {
        throw new Error(err.response?.data?.error || "Login failed")
      }
    },
    logout() {
      this.currentUser = null
    },
    async registerHospital(formData) {
      try {
        const res = await axios.post('/api/register-hospital', formData)
        return res.data
      } catch (err) {
        throw new Error(err.response?.data?.error || "Registration failed")
      }
    },

    // --- ADMIN ACTIONS ---
    async fetchUnverified() {
      try {
        const res = await axios.get('/api/admin/unverified')
        this.unverifiedHospitals = res.data
      } catch (err) {
        console.error("Failed to fetch unverified hospitals")
      }
    },
    async verifyHospital(id) {
      try {
        await axios.post(`/api/admin/verify/${id}`)
        // Remove it from the local list
        this.unverifiedHospitals = this.unverifiedHospitals.filter(h => h.id !== id)
      } catch (err) {
        alert("Verification failed")
      }
    },



















    //  in hospitalStore.js:
    
    async addCustomResource(hospitalId, resourceData) {
      try {
        await axios.post(`/api/hospital/${hospitalId}/add-resource`, resourceData)
      } catch (err) {
        throw new Error(err.response?.data?.error || "Failed to add resource")
      }
    },
    async reportSpamUser(hospitalId, mobile) {
      try {
        const res = await axios.post('/api/hospital/report-user', { hospital_id: hospitalId, mobile })
        alert(res.data.message)
      } catch (err) {
        alert(err.response?.data?.error || "Failed to report user")
      }
    },
    async fetchUserReports() {
      try {
        const res = await axios.get('/api/admin/reports')
        return res.data
      } catch (err) {
        console.error("Failed to fetch reports")
        return []
      }
    },
    async banUser(reportId) {
      try {
        await axios.post(`/api/admin/block-user/${reportId}`)
      } catch (err) {
        alert("Failed to block user")
      }
    },









    
    async fetchMyApplications(mobile) {
      try {
        const res = await axios.get(`/api/my-applications?mobile=${mobile}`)
        this.myApplications = res.data
      } catch (err) {
        console.error("Failed to fetch applications", err)
      }
    },
    async cancelApplication(token) {
      try {
        const res = await axios.post('/api/cancel-request', { token })
        return res.data
      } catch (err) {
        throw new Error(err.response?.data?.error || "Failed to cancel request.")
      }
    },





    
    async deleteCustomResource(hospitalId, type) {
      try {
        // We use encodeURIComponent in case the resource type has spaces (e.g., "ICU Bed")
        await axios.delete(`/api/hospital/${hospitalId}/resource/${encodeURIComponent(type)}`)
      } catch (err) {
        throw new Error(err.response?.data?.error || "Failed to delete resource")
      }
    }

















  }
})
  

