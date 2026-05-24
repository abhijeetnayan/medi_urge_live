import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'


import SearchView from './views/SearchView.vue'
import AdminDashboard from './views/AdminDashboard.vue'
//import HospitalDetail from './views/HospitalDetail.vue'
import HospitalDashboard from './views/HospitalDashboard.vue'

const routes = [
  { path: '/', component: SearchView },
  { path: '/admin', component: AdminDashboard },
  //{path: '/hospital/:id', component: HospitalDetail }
  { path: '/hospital/:id/dashboard', component: HospitalDashboard } // The :id is crucial!
  
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
