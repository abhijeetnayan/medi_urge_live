<template>
  <div class="container py-5 min-vh-100">
    <div class="row justify-content-center mb-5 text-center">
      <div class="col-lg-8">
        <h1 class="display-4 fw-black mb-3 text-dark">Meet the Developers</h1>
        <p class="lead text-muted">The Nebula Navigators architecting the future of emergency response.</p>
        <hr class="w-25 mx-auto text-primary border-2 opacity-50">
      </div>
    </div>

    <div class="row justify-content-center g-4">
      
      <div v-for="member in team" :key="member.name" class="col-md-6 col-lg-4 d-flex">
        <div class="card shadow-sm border-0 w-100 rounded-4 overflow-hidden team-card">
          
          <div class="bg-dark text-white p-4 text-center position-relative">
            <h4 class="fw-bold mb-0" style="letter-spacing: 1px;">{{ member.name }}</h4>
            <p class="text-uppercase tracking-wider small text-light opacity-75 mt-2 mb-0">
              {{ member.role }}
            </p>
          </div>
          
          <div class="card-body p-4 text-center d-flex flex-column">
            <p class="text-muted mb-4 flex-grow-1" style="font-size: 0.95rem; line-height: 1.6;">
              {{ member.bio }}
            </p>
            
            <hr class="w-75 mx-auto mb-4 opacity-25">
            
            <div class="d-flex justify-content-center gap-3 mt-auto">
              <a :href="member.github" target="_blank" class="btn btn-outline-dark rounded-circle d-flex align-items-center justify-content-center" style="width: 45px; height: 45px;" title="GitHub">GitHub
                <i class="bi bi-github fs-5"></i>
              </a>
              <a :href="member.linkedin" target="_blank" class="btn btn-outline-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 45px; height: 45px;" title="LinkedIn">linkedin
                <i class="bi bi-linkedin fs-5"></i>
              </a>
            </div>
          </div>
          
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// This is your single source of truth. Edit your team details right here.
const team = ref([
  {
    name: 'Abhijeet Nayan',
    role: 'Lead Full-Stack Engineer',
    bio: 'Engineered the real-time Redis token handshake and deployed the PostgreSQL cloud backend concurrently while pursuing dual degrees in Civil Engineering and Data Science.',
    github: 'https://github.com/abhijeetnayan',
    linkedin: 'https://www.linkedin.com/in/abhijeet-nayan-27a291178?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app'
  },
  {
    name: 'Suraj Kumar pathak',
    role: 'UI/UX Designer',
    bio: 'Designed the responsive Vue 3 UI, integrated the dynamic Leaflet map, and ensured seamless component state management using Pinia.',
    github: '#',
    linkedin: '#'
  },
  {
    name: 'Anmol',
    role: 'Database Administrator',
    bio: 'Architected the SQLite/PostgreSQL data models, managed the SQLAlchemy ORM relations, and ensured robust auditing and logging systems.',
    github: '#',
    linkedin: '#'
  },
  {
    name: 'Rishav',
    role: 'Frontend Architect',
    bio: 'Created the wireframes, established the visual hierarchy, and implemented the Bootstrap 5 design system to ensure accessibility during high-stress medical emergencies.',
    github: '#',
    linkedin: '#'
  },
  {
    name: 'Anshu raj',
    role: 'Project Manager & QA',
    bio: 'Coordinated the agile development sprints, handled deployment pipelines via Vercel and Render, and conducted rigorous cross-browser testing.',
    github: '#',
    linkedin: '#'
  }
])
</script>

<style scoped>
.fw-black {
  font-weight: 900;
}
.tracking-wider {
  letter-spacing: 0.1em;
}
/* Subtle hover effect to make the cards feel premium */
.team-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
}
</style>
