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
    
    localStorage.setItem('artfolio_token', data.access_token)
    router.push('/dashboard')
  } catch (err) {
    console.warn("API login failed, falling back to mock authentication:", err)
    if (email.value === 'artista@artfolio.com' && password.value === 'artista123') {
      localStorage.setItem('artfolio_token', 'mock-jwt-token-for-demo')
      router.push('/dashboard')
    } else {
      error.value = "Error de conexión. Para demostración local, usa: artista@artfolio.com / artista123"
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrapper classic-cursor">
    
    <!-- Background halftone decoration consistent with desktop -->
    <div class="starburst-bg"></div>

    <!-- Windows 95 Network Login Box (Center of screen) -->
    <div class="win95-window login-dialog win95-outset">
      <div class="win95-title-bar">
        <div class="win95-title-text">🔑 Enter Network Password</div>
        <div class="win95-title-bar-controls">
          <router-link to="/" class="win95-btn close-btn-link">X</router-link>
        </div>
      </div>

      <div class="win95-window-content login-body">
        
        <!-- Left Column: Win95 Network Icon -->
        <div class="login-icon-column">
          <!-- Retro key and computer layout -->
          <div class="pixel-key-icon">🔑</div>
          <div class="pixel-pc-icon">🖳</div>
        </div>

        <!-- Right Column: Login form and messages -->
        <div class="login-form-column">
          <p class="login-prompt-text">
            Enter your network password to log in to the ArtFolio Administrative Dashboard.
          </p>

          <form @submit.prevent="handleLogin" class="login-form">
            <!-- Retro Error Box -->
            <div v-if="error" class="win95-window error-box-win win95-outset">
              <div class="error-box-header">
                <span class="warning-icon">⚠️</span> System Message
              </div>
              <div class="error-box-content">
                {{ error }}
              </div>
            </div>

            <div class="form-row">
              <label for="email" class="form-label">Resource:</label>
              <span class="resource-name">ArtFolio CMS Portal</span>
            </div>

            <div class="form-row">
              <label for="email" class="form-label">User name:</label>
              <input 
                type="email" 
                id="email" 
                v-model="email" 
                required 
                placeholder="artista@artfolio.com"
                class="win95-inset win95-textbox"
              />
            </div>
            
            <div class="form-row">
              <label for="password" class="form-label">Password:</label>
              <input 
                type="password" 
                id="password" 
                v-model="password" 
                required 
                placeholder="••••••••"
                class="win95-inset win95-textbox"
              />
            </div>

            <!-- Double-bevel login action buttons -->
            <div class="form-actions">
              <button type="submit" class="win95-btn action-ok-btn" :disabled="loading">
                <span v-if="loading" class="btn-spinner"></span>
                <span v-else>OK</span>
              </button>
              <router-link to="/" class="win95-btn action-cancel-btn">
                Cancel
              </router-link>
            </div>
          </form>
        </div>

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
  position: relative;
  width: 100vw;
  box-sizing: border-box;
  padding: 20px;
}

/* Background starburst clip path styling matching public view */
.starburst-bg {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 700px;
  height: 700px;
  background-color: var(--y2k-yellow);
  clip-path: polygon(
    50% 0%, 54% 33%, 80% 12%, 67% 43%, 100% 50%, 67% 57%, 80% 88%, 54% 67%, 
    50% 100%, 46% 67%, 20% 88%, 33% 57%, 0% 50%, 33% 43%, 20% 12%, 46% 33%
  );
  filter: drop-shadow(0 0 40px rgba(255, 230, 0, 0.4));
  z-index: 1;
  pointer-events: none;
}

.login-dialog {
  width: 440px;
  z-index: 10;
  position: relative;
  font-family: 'Tahoma', 'MS Sans Serif', sans-serif;
}

.close-btn-link {
  text-decoration: none;
  font-size: 10px;
}

.login-body {
  display: flex;
  padding: 12px;
  gap: 15px;
  background-color: var(--win-grey);
}

/* Column layout */
.login-icon-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  width: 48px;
}

.pixel-key-icon {
  font-size: 2.2rem;
}

.pixel-pc-icon {
  font-size: 2.2rem;
}

.login-form-column {
  flex-grow: 1;
}

.login-prompt-text {
  font-size: 11px;
  line-height: 1.4;
  margin: 0 0 12px 0;
  color: #000000;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Form row elements */
.form-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-label {
  width: 75px;
  font-size: 11px;
  color: #000000;
  text-align: right;
  flex-shrink: 0;
}

.resource-name {
  font-weight: bold;
  font-size: 11px;
  color: #555555;
}

.win95-textbox {
  flex-grow: 1;
  padding: 3px 6px;
  font-size: 11px;
  outline: none;
  background-color: #ffffff;
  color: #000000;
  border: 2px inset var(--win-grey);
  box-sizing: border-box;
}

.win95-textbox:focus {
  background-color: #ffffdd; /* Subtle vintage yellow highlight */
}

/* Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 15px;
}

.action-ok-btn, .action-cancel-btn {
  padding: 4px 20px;
  font-size: 11px;
  font-weight: bold;
  min-width: 80px;
  text-align: center;
  text-decoration: none;
}

/* Win95 Dialog error styling */
.error-box-win {
  margin-bottom: 10px;
  border: 2px solid #800000 !important;
  box-shadow: 2px 2px 0px #000000;
}

.error-box-header {
  background-color: #800000;
  color: #ffffff;
  font-size: 10px;
  font-weight: bold;
  padding: 2px 4px;
}

.error-box-content {
  padding: 6px;
  font-size: 10px;
  color: #800000;
  background-color: #ffdddd;
  line-height: 1.3;
}

/* Spinner anim */
.btn-spinner {
  width: 10px;
  height: 10px;
  border: 1.5px solid rgba(0, 0, 0, 0.2);
  border-top: 1.5px solid #000000;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
