<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const API_URL = 'http://localhost:8000'
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || 'Credenciales inválidas')
    }
    
    // Save JWT token in localStorage
    localStorage.setItem('artfolio_token', data.access_token)
    
    // Redirect to private Admin Dashboard
    router.push('/dashboard')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrapper">
    <div class="cybersigil-bg"></div>
    
    <div class="login-card">
      <!-- Cybersigil design borders -->
      <div class="sigil-decor top-left"></div>
      <div class="sigil-decor top-right"></div>
      <div class="sigil-decor bottom-left"></div>
      <div class="sigil-decor bottom-right"></div>
      
      <header class="card-header">
        <h2 class="title">Acceso Artista</h2>
        <p class="subtitle">Ingresa tus credenciales para administrar el catálogo</p>
      </header>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <!-- Error alert -->
        <div v-if="error" class="error-alert">
          <span class="warning-icon">⚠️</span> {{ error }}
        </div>
        
        <div class="form-group">
          <label for="email">Correo Electrónico</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            required 
            placeholder="artista@artfolio.com"
            class="input-field"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Contraseña</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required 
            placeholder="••••••••"
            class="input-field"
          />
        </div>
        
        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Iniciar Sesión</span>
        </button>
      </form>
      
      <div class="back-link-container">
        <router-link to="/" class="back-link">← Volver a la Galería</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #f4f0e6;
  padding: 1.5rem;
  box-sizing: border-box;
  width: 100%;
}

.cybersigil-bg {
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at center, rgba(107, 29, 47, 0.06) 0%, transparent 80%),
              #0d0d0c;
  z-index: -1;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(28, 27, 24, 0.85);
  border: 1px solid rgba(197, 160, 89, 0.2);
  padding: 2.5rem 2rem;
  box-sizing: border-box;
  position: relative;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
}

/* Y2K Cybersigil Decors */
.sigil-decor {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 1.5px solid #c5a059;
  pointer-events: none;
}

.sigil-decor.top-left {
  top: -4px;
  left: -4px;
  border-right: none;
  border-bottom: none;
}

.sigil-decor.top-right {
  top: -4px;
  right: -4px;
  border-left: none;
  border-bottom: none;
}

.sigil-decor.bottom-left {
  bottom: -4px;
  left: -4px;
  border-right: none;
  border-top: none;
}

.sigil-decor.bottom-right {
  bottom: -4px;
  right: -4px;
  border-left: none;
  border-top: none;
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.title {
  font-family: 'Cinzel', serif;
  font-size: 1.8rem;
  color: #c5a059;
  margin-bottom: 0.5rem;
  letter-spacing: 0.1em;
}

.subtitle {
  font-family: 'Outfit', sans-serif;
  font-size: 0.8rem;
  color: #a39b8c;
  font-weight: 300;
  line-height: 1.4;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.error-alert {
  background: rgba(107, 29, 47, 0.2);
  border: 1px solid #6b1d2f;
  color: #fda4af;
  padding: 0.75rem;
  font-size: 0.8rem;
  font-family: 'Outfit', sans-serif;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-family: 'Cinzel', serif;
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  color: #c5a059;
  text-transform: uppercase;
}

.input-field {
  background: rgba(13, 13, 12, 0.7);
  border: 1px solid rgba(197, 160, 89, 0.25);
  color: #f4f0e6;
  padding: 0.75rem 1rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.input-field:focus {
  outline: none;
  border-color: #c5a059;
  box-shadow: 0 0 8px rgba(197, 160, 89, 0.2);
  background: #0d0d0c;
}

.btn-submit {
  background: #6b1d2f;
  border: 1px solid #c5a059;
  color: #f4f0e6;
  padding: 0.8rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 0.5rem;
}

.btn-submit:hover:not(:disabled) {
  background: #800020;
  box-shadow: 0 0 10px rgba(197, 160, 89, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.back-link-container {
  text-align: center;
  margin-top: 1.5rem;
}

.back-link {
  color: #a39b8c;
  text-decoration: none;
  font-size: 0.8rem;
  font-family: 'Outfit', sans-serif;
  transition: color 0.3s;
}

.back-link:hover {
  color: #c5a059;
}

/* Spinner anim */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(244, 240, 230, 0.2);
  border-top: 2px solid #f4f0e6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
