<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

// Detect theme from query param (?theme=gothic) or localStorage fallback
const isGothic = computed(() =>
  route.query.theme === 'gothic' ||
  (!route.query.theme && localStorage.getItem('artfolio_theme') === 'gothic')
)

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Credenciales inválidas')
    }

    localStorage.setItem('artfolio_token', data.access_token)
    router.push('/dashboard')
  } catch (err) {
    console.warn('API login failed, falling back to mock authentication:', err)
    if (email.value === 'artista@artfolio.com' && password.value === 'artista123') {
      localStorage.setItem('artfolio_token', 'mock-jwt-token-for-demo')
      router.push('/dashboard')
    } else {
      error.value = 'Error de conexión. Para demostración local, usa: artista@artfolio.com / artista123'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>

  <!-- ═══════════════════════════════════════════════ -->
  <!-- GOTHIC / CYBERSIGIL LOGIN                       -->
  <!-- ═══════════════════════════════════════════════ -->
  <div v-if="isGothic" class="gothic-login-wrapper">

    <!-- Animated background grid -->
    <div class="gothic-grid-bg"></div>

    <!-- Sigil ring decorations -->
    <div class="sigil-ring sigil-ring-1"></div>
    <div class="sigil-ring sigil-ring-2"></div>

    <!-- Top ornament line -->
    <div class="gothic-ornament-top">
      <svg viewBox="0 0 1000 40" preserveAspectRatio="none">
        <path d="M 0 20 L 400 20 L 420 10 L 450 30 L 460 15 L 480 25 L 500 0 L 520 25 L 540 15 L 550 30 L 580 10 L 600 20 L 1000 20"
          fill="none" stroke="#c5a059" stroke-width="1.5" />
        <circle cx="500" cy="0" r="4" fill="#c5a059" />
      </svg>
    </div>

    <!-- Login card -->
    <div class="gothic-login-card">

      <!-- Header -->
      <div class="gothic-card-header">
        <div class="gothic-sigil-glyph">⬡</div>
        <h1 class="gothic-card-title">Portal del Artista</h1>
        <p class="gothic-card-subtitle">Autentificación de acceso al Santuario</p>
        <div class="gothic-separator">
          <span class="sep-line"></span>
          <span class="sep-glyph">✦</span>
          <span class="sep-line"></span>
        </div>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="gothic-form">

        <!-- Error message -->
        <div v-if="error" class="gothic-error-box">
          <span class="gothic-error-icon">⚠</span>
          <span class="gothic-error-text">{{ error }}</span>
        </div>

        <div class="gothic-field">
          <label for="g-email" class="gothic-label">✉ Correo del Artista</label>
          <input
            type="email"
            id="g-email"
            v-model="email"
            required
            placeholder="artista@artfolio.com"
            class="gothic-input"
            autocomplete="username"
          />
        </div>

        <div class="gothic-field">
          <label for="g-password" class="gothic-label">🔒 Contraseña Ritual</label>
          <input
            type="password"
            id="g-password"
            v-model="password"
            required
            placeholder="••••••••"
            class="gothic-input"
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="gothic-submit-btn" :disabled="loading">
          <span v-if="loading" class="gothic-spinner"></span>
          <span v-else>⟶ Invocar Acceso</span>
        </button>

      </form>

      <!-- Footer link back -->
      <div class="gothic-card-footer">
        <router-link to="/" class="gothic-back-link">← Regresar a la Galería</router-link>
      </div>

    </div>

    <!-- Bottom ornament line -->
    <div class="gothic-ornament-bottom">
      <svg viewBox="0 0 1000 40" preserveAspectRatio="none">
        <path d="M 0 20 L 400 20 L 420 10 L 450 30 L 460 15 L 480 25 L 500 40 L 520 25 L 540 15 L 550 30 L 580 10 L 600 20 L 1000 20"
          fill="none" stroke="#c5a059" stroke-width="1.5" />
        <circle cx="500" cy="40" r="4" fill="#c5a059" />
      </svg>
    </div>

  </div>

  <!-- ═══════════════════════════════════════════════ -->
  <!-- Y2K / WIN95 LOGIN                              -->
  <!-- ═══════════════════════════════════════════════ -->
  <div v-else class="login-wrapper classic-cursor">

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
              <div class="error-box-content">{{ error }}</div>
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
              <router-link to="/" class="win95-btn action-cancel-btn">Cancel</router-link>
            </div>
          </form>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
/* ════════════════════════════════════
   GOTHIC / CYBERSIGIL STYLES
   ════════════════════════════════════ */
.gothic-login-wrapper {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #0a0a0f;
  position: relative;
  overflow: hidden;
  font-family: 'Cinzel', 'Palatino Linotype', serif;
}

.gothic-grid-bg {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(197,160,89,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(197,160,89,0.06) 1px, transparent 1px);
  background-size: 40px 40px;
  z-index: 0;
  pointer-events: none;
  animation: gridScroll 20s linear infinite;
}

@keyframes gridScroll {
  0%   { background-position: 0 0; }
  100% { background-position: 0 40px; }
}

/* Decorative animated sigil rings */
.sigil-ring {
  position: fixed;
  border-radius: 50%;
  border: 1px solid rgba(197,160,89,0.12);
  pointer-events: none;
  z-index: 0;
}
.sigil-ring-1 {
  width: 600px; height: 600px;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  animation: rotateSlow 40s linear infinite;
}
.sigil-ring-2 {
  width: 400px; height: 400px;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  border-color: rgba(80,0,120,0.2);
  animation: rotateSlow 25s linear infinite reverse;
}
@keyframes rotateSlow {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to   { transform: translate(-50%, -50%) rotate(360deg); }
}

/* Ornament lines */
.gothic-ornament-top,
.gothic-ornament-bottom {
  position: fixed;
  left: 0; right: 0;
  height: 40px;
  z-index: 1;
  pointer-events: none;
}
.gothic-ornament-top  { top: 0; }
.gothic-ornament-bottom { bottom: 0; }
.gothic-ornament-top svg,
.gothic-ornament-bottom svg { width: 100%; height: 40px; }

/* ── Login Card ── */
.gothic-login-card {
  position: relative;
  z-index: 10;
  width: 420px;
  background: linear-gradient(160deg, #12101a 0%, #0e0c18 60%, #100a1c 100%);
  border: 1px solid rgba(197,160,89,0.3);
  box-shadow:
    0 0 40px rgba(197,160,89,0.08),
    0 0 80px rgba(80,0,120,0.15),
    inset 0 1px 0 rgba(197,160,89,0.1);
  padding: 36px 40px 28px;
}

/* Card header */
.gothic-card-header {
  text-align: center;
  margin-bottom: 28px;
}

.gothic-sigil-glyph {
  font-size: 2.5rem;
  color: #c5a059;
  line-height: 1;
  margin-bottom: 10px;
  filter: drop-shadow(0 0 8px rgba(197,160,89,0.6));
  animation: glyphPulse 3s ease-in-out infinite;
}
@keyframes glyphPulse {
  0%, 100% { filter: drop-shadow(0 0 8px rgba(197,160,89,0.4)); }
  50%       { filter: drop-shadow(0 0 18px rgba(197,160,89,0.9)); }
}

.gothic-card-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #e8d5a3;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin: 0 0 6px;
  text-shadow: 0 0 20px rgba(197,160,89,0.3);
}

.gothic-card-subtitle {
  font-size: 0.72rem;
  color: #7a6a4a;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin: 0 0 18px;
}

.gothic-separator {
  display: flex;
  align-items: center;
  gap: 10px;
}
.sep-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(197,160,89,0.4), transparent);
}
.sep-glyph {
  color: #c5a059;
  font-size: 0.8rem;
}

/* ── Form ── */
.gothic-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.gothic-error-box {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: rgba(120,0,0,0.25);
  border: 1px solid rgba(200,50,50,0.4);
  padding: 10px 14px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.75rem;
  color: #e07070;
  line-height: 1.4;
}
.gothic-error-icon { flex-shrink: 0; font-size: 1rem; }

.gothic-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.gothic-label {
  font-size: 0.68rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #7a6a4a;
  font-family: 'Share Tech Mono', 'Cinzel', serif;
}

.gothic-input {
  background: rgba(10,8,20,0.8);
  border: 1px solid rgba(197,160,89,0.25);
  border-bottom-color: rgba(197,160,89,0.5);
  color: #e8d5a3;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.9rem;
  padding: 10px 14px;
  outline: none;
  transition: border-color 0.25s, box-shadow 0.25s;
}
.gothic-input::placeholder { color: rgba(197,160,89,0.25); }
.gothic-input:focus {
  border-color: rgba(197,160,89,0.7);
  box-shadow: 0 0 12px rgba(197,160,89,0.15), inset 0 0 8px rgba(197,160,89,0.05);
}

.gothic-submit-btn {
  margin-top: 8px;
  padding: 13px;
  background: linear-gradient(135deg, rgba(197,160,89,0.12) 0%, rgba(80,0,120,0.15) 100%);
  border: 1px solid rgba(197,160,89,0.4);
  color: #e8d5a3;
  font-family: 'Cinzel', 'Palatino Linotype', serif;
  font-size: 0.85rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.gothic-submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(197,160,89,0.22) 0%, rgba(100,0,160,0.25) 100%);
  border-color: rgba(197,160,89,0.7);
  box-shadow: 0 0 20px rgba(197,160,89,0.2), 0 0 40px rgba(80,0,120,0.15);
  color: #fff8e7;
}
.gothic-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.gothic-spinner {
  width: 14px; height: 14px;
  border: 1.5px solid rgba(197,160,89,0.2);
  border-top-color: #c5a059;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

/* Card footer */
.gothic-card-footer {
  text-align: center;
  margin-top: 22px;
  padding-top: 16px;
  border-top: 1px solid rgba(197,160,89,0.1);
}
.gothic-back-link {
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #5a4a2a;
  text-decoration: none;
  transition: color 0.2s;
}
.gothic-back-link:hover { color: #c5a059; }

/* ════════════════════════════════════
   Y2K / WIN95 STYLES  (unchanged)
   ════════════════════════════════════ */
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

.starburst-bg {
  position: fixed;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 700px; height: 700px;
  background-color: var(--y2k-yellow);
  clip-path: polygon(
    50% 0%, 54% 33%, 80% 12%, 67% 43%, 100% 50%, 67% 57%, 80% 88%, 54% 67%,
    50% 100%, 46% 67%, 20% 88%, 33% 57%, 0% 50%, 33% 43%, 20% 12%, 46% 33%
  );
  filter: drop-shadow(0 0 40px rgba(255,230,0,0.4));
  z-index: 1;
  pointer-events: none;
}

.login-dialog {
  width: 440px;
  z-index: 10;
  position: relative;
  font-family: 'Tahoma', 'MS Sans Serif', sans-serif;
}

.close-btn-link { text-decoration: none; font-size: 10px; }

.login-body {
  display: flex;
  padding: 12px;
  gap: 15px;
  background-color: var(--win-grey);
}

.login-icon-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  width: 48px;
}

.pixel-key-icon, .pixel-pc-icon { font-size: 2.2rem; }

.login-form-column { flex-grow: 1; }

.login-prompt-text {
  font-size: 11px;
  line-height: 1.4;
  margin: 0 0 12px;
  color: #000000;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

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

.resource-name { font-weight: bold; font-size: 11px; color: #555555; }

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
.win95-textbox:focus { background-color: #ffffdd; }

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

/* Shared spinner */
.btn-spinner {
  width: 10px; height: 10px;
  border: 1.5px solid rgba(0,0,0,0.2);
  border-top: 1.5px solid #000000;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  0%   { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
