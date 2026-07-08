<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'

// API base URL
const API_URL = 'http://localhost:8000'

// State variables
const artworks = ref([])
const collections = ref([])
const activeCollectionId = ref(null)
const loading = ref(true)

// Search & filter states
const searchQuery = ref('')
const selectedAvailability = ref('')
const selectedSort = ref('newest')

// UI States
const selectedArtwork = ref(null)
const monitorPower = ref(true)
const showWelcome = ref(true)
const showStartMenu = ref(false)
const showWarningPopup = ref(false)
const clockTime = ref('')

// Draggable window coordinates
const positions = ref({
  welcome: { x: 280, y: 150 },
  wordart: { x: 40, y: 30 },
  smiley: { x: 820, y: 40 },
  warning: { x: 50, y: 600 },
  year: { x: 820, y: 600 },
  textedit: { x: 480, y: 550 },
  warningPopup: { x: 300, y: 300 }
})

// Draggable stickers
const stickers = ref([
  { id: 1, text: "Esouth on the track ⚡", x: 380, y: 40, rotation: -12, colorClass: "pink-vibe" },
  { id: 2, text: "Born to Ride 🏁", x: 830, y: 250, rotation: 8, colorClass: "blue-vibe" },
  { id: 3, text: "COMING SOON ☄️", x: 140, y: 320, rotation: -15, colorClass: "yellow-vibe" },
  { id: 4, text: "Cyber Vibe 👾", x: 830, y: 440, rotation: -5, colorClass: "pink-vibe" }
])

// Background Cyber Stars
const cyberStars = ref([
  { id: 1, x: 80, y: 180, size: 45, color: '#ffff00', duration: '6s' },
  { id: 2, x: 150, y: 500, size: 65, color: '#ff00ff', duration: '8s' },
  { id: 3, x: 740, y: 190, size: 55, color: '#ff00ff', duration: '10s' },
  { id: 4, x: 920, y: 420, size: 40, color: '#ffff00', duration: '5s' },
  { id: 5, x: 720, y: 540, size: 30, color: '#00ffff', duration: '7s' }
])

// Drawing Canvas States
const canvasRef = ref(null)
const ctx = ref(null)
const drawing = ref(false)
const brushColor = ref('#ff00ff') // neon magenta default
const activeTool = ref('brush') // 'pencil', 'brush', 'eraser'
const brushSize = ref(4)

// Fallback Mock Data
const mockCollections = [
  { id: 1, nombre: "Mitologías Perdidas", descripcion: "Exploraciones pictóricas de mitos olvidados en el tiempo." },
  { id: 2, nombre: "Anatomía de la Melancolía", descripcion: "Estudios anatómicos y claroscuro de emociones humanas profundas." }
]

const mockArtworks = [
  {
    id: 101,
    titulo: "El Lamento de Ícaro",
    tecnica: "Óleo sobre lienzo",
    dimensiones: "120 x 90 cm",
    ano: 2024,
    precio: 1200.00,
    imagen_url: "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?q=80&w=600&auto=format&fit=crop",
    estado: "Disponible",
    coleccion_id: 1,
    created_at: "2026-06-01T12:00:00Z"
  },
  {
    id: 102,
    titulo: "Estudio de las Sombras",
    tecnica: "Carboncillo sobre papel hecho a mano",
    dimensiones: "40 x 30 cm",
    ano: 2023,
    precio: 350.00,
    imagen_url: "https://images.unsplash.com/photo-1579783928621-7a13d66a62d1?q=80&w=600&auto=format&fit=crop",
    estado: "En exhibición",
    coleccion_id: 2,
    created_at: "2026-06-02T12:00:00Z"
  },
  {
    id: 103,
    titulo: "Memento Mori II",
    tecnica: "Óleo y pan de oro",
    dimensiones: "80 x 80 cm",
    ano: 2025,
    precio: 950.00,
    imagen_url: "https://images.unsplash.com/photo-1580136579312-94651dfd596d?q=80&w=600&auto=format&fit=crop",
    estado: "Vendida",
    coleccion_id: 1,
    created_at: "2026-06-03T12:00:00Z"
  },
  {
    id: 104,
    titulo: "La Cámara del Erudito",
    tecnica: "Acrílico sobre madera",
    dimensiones: "100 x 75 cm",
    ano: 2024,
    precio: 800.00,
    imagen_url: "https://images.unsplash.com/photo-1605721911519-3dfeb3be25e7?q=80&w=600&auto=format&fit=crop",
    estado: "Disponible",
    coleccion_id: 2,
    created_at: "2026-06-04T12:00:00Z"
  },
  {
    id: 105,
    titulo: "Sinfonía del Crepúsculo",
    tecnica: "Óleo sobre lienzo grueso",
    dimensiones: "150 x 120 cm",
    ano: 2025,
    precio: 2400.00,
    imagen_url: "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?q=80&w=600&auto=format&fit=crop",
    estado: "Disponible",
    coleccion_id: 1,
    created_at: "2026-06-05T12:00:00Z"
  }
]

// Drag-and-drop mechanics
const activeDrag = ref(null)

const startDrag = (event, type, key) => {
  event.preventDefault()
  let clientX = event.clientX
  let clientY = event.clientY
  if (event.touches && event.touches.length > 0) {
    clientX = event.touches[0].clientX
    clientY = event.touches[0].clientY
  }

  let currentX, currentY
  if (type === 'window') {
    currentX = positions.value[key].x
    currentY = positions.value[key].y
  } else {
    const idx = stickers.value.findIndex(s => s.id === key)
    currentX = stickers.value[idx].x
    currentY = stickers.value[idx].y
  }

  activeDrag.value = {
    type,
    key,
    offsetX: clientX - currentX,
    offsetY: clientY - currentY
  }

  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', handleDrag, { passive: false })
  document.addEventListener('touchend', stopDrag)
}

const handleDrag = (event) => {
  if (!activeDrag.value) return
  let clientX = event.clientX
  let clientY = event.clientY
  if (event.touches && event.touches.length > 0) {
    clientX = event.touches[0].clientX
    clientY = event.touches[0].clientY
  }

  const newX = clientX - activeDrag.value.offsetX
  const newY = clientY - activeDrag.value.offsetY

  if (activeDrag.value.type === 'window') {
    positions.value[activeDrag.value.key].x = newX
    positions.value[activeDrag.value.key].y = newY
  } else {
    const idx = stickers.value.findIndex(s => s.id === activeDrag.value.key)
    if (idx !== -1) {
      stickers.value[idx].x = newX
      stickers.value[idx].y = newY
    }
  }
}

const stopDrag = () => {
  activeDrag.value = null
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', handleDrag)
  document.removeEventListener('touchend', stopDrag)
}

// Fetch data from API with fallback
const fetchData = async () => {
  loading.value = true
  try {
    const artworksRes = await fetch(`${API_URL}/artworks/`)
    if (!artworksRes.ok) throw new Error("No se pudo conectar al servidor de obras")
    artworks.value = await artworksRes.json()

    const collectionsRes = await fetch(`${API_URL}/collections/`)
    if (!collectionsRes.ok) throw new Error("No se pudo conectar al servidor de colecciones")
    collections.value = await collectionsRes.json()
  } catch (err) {
    console.warn("API offline or error, falling back to mock data.", err)
    artworks.value = mockArtworks
    collections.value = mockCollections
  } finally {
    loading.value = false
    // Load first artwork on load
    if (artworks.value.length > 0) {
      selectArtwork(artworks.value[0])
    } else {
      initCanvas()
    }
  }
}

// Select collection to filter
const setCollection = (id) => {
  activeCollectionId.value = id
}

// Computed property to filter artworks
const filteredArtworks = computed(() => {
  let list = [...artworks.value]
  
  if (activeCollectionId.value !== null) {
    list = list.filter(artwork => artwork.coleccion_id === activeCollectionId.value)
  }
  
  if (searchQuery.value.trim() !== '') {
    const q = searchQuery.value.toLowerCase().trim()
    list = list.filter(artwork => 
      artwork.titulo.toLowerCase().includes(q) || 
      artwork.tecnica.toLowerCase().includes(q)
    )
  }
  
  if (selectedAvailability.value !== '') {
    list = list.filter(artwork => artwork.estado === selectedAvailability.value)
  }
  
  list.sort((a, b) => {
    if (selectedSort.value === 'newest') {
      return new Date(b.created_at || 0) - new Date(a.created_at || 0)
    } else if (selectedSort.value === 'oldest') {
      return new Date(a.created_at || 0) - new Date(b.created_at || 0)
    } else if (selectedSort.value === 'price-asc') {
      const pA = a.precio !== null ? parseFloat(a.precio) : Infinity
      const pB = b.precio !== null ? parseFloat(b.precio) : Infinity
      return pA - pB
    } else if (selectedSort.value === 'price-desc') {
      const pA = a.precio !== null ? parseFloat(a.precio) : -Infinity
      const pB = b.precio !== null ? parseFloat(b.precio) : -Infinity
      return pB - pA
    }
    return 0
  })
  
  return list
})

// Select Artwork file
const selectArtwork = (art) => {
  selectedArtwork.value = art
  drawArtworkOnCanvas()
}

// WhatsApp link generator
const getWhatsAppLink = (artwork) => {
  const phoneNumber = '521234567890'
  const text = encodeURIComponent(
    `Hola, estoy interesado en adquirir tu obra de arte "${artwork.titulo}" (${artwork.tecnica}, ${artwork.dimensiones}) catalogada en tu portafolio ArtFolio.`
  )
  return `https://wa.me/${phoneNumber}?text=${text}`
}

// Start menu trigger
const toggleStartMenu = () => {
  showStartMenu.value = !showStartMenu.value
}

// Power off monitor switch
const toggleMonitorPower = () => {
  monitorPower.value = !monitorPower.value
}

// Clock logic
const updateClock = () => {
  const now = new Date()
  let hours = now.getHours()
  const ampm = hours >= 12 ? 'PM' : 'AM'
  hours = hours % 12
  hours = hours ? hours : 12 // the hour '0' should be '12'
  const minutes = now.getMinutes().toString().padStart(2, '0')
  clockTime.value = `${hours}:${minutes} ${ampm}`
}

// Canvas Painting Logic
const initCanvas = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  ctx.value = canvas.getContext('2d', { willReadFrequently: true })
  
  canvas.width = 440
  canvas.height = 290
  
  clearPaintArea()
}

const clearPaintArea = () => {
  if (!ctx.value || !canvasRef.value) return
  ctx.value.fillStyle = '#ffffff'
  ctx.value.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  
  // If no artwork loaded, draw default "COMING SOON" Y2K logo
  if (!selectedArtwork.value) {
    drawDefaultStarburst()
  }
}

const drawDefaultStarburst = () => {
  const canvas = canvasRef.value
  const cx = canvas.width / 2
  const cy = canvas.height / 2
  
  // Starburst
  ctx.value.fillStyle = '#ff00ff'
  ctx.value.beginPath()
  const spikes = 20
  const outerRadius = 100
  const innerRadius = 70
  let rot = Math.PI / 2 * 3
  const step = Math.PI / spikes
  
  ctx.value.moveTo(cx, cy - outerRadius)
  for (let i = 0; i < spikes; i++) {
    let x = cx + Math.cos(rot) * outerRadius
    let y = cy + Math.sin(rot) * outerRadius
    ctx.value.lineTo(x, y)
    rot += step
    
    x = cx + Math.cos(rot) * innerRadius
    y = cy + Math.sin(rot) * innerRadius
    ctx.value.lineTo(x, y)
    rot += step
  }
  ctx.value.lineTo(cx, cy - outerRadius)
  ctx.value.closePath()
  ctx.value.fill()
  
  // Text shadow/glow
  ctx.value.fillStyle = '#000000'
  ctx.value.font = 'bold 36px "VT323", monospace'
  ctx.value.textAlign = 'center'
  ctx.value.fillText('COMING SOON', cx + 3, cy + 13)
  
  ctx.value.fillStyle = '#ffff00'
  ctx.value.fillText('COMING SOON', cx, cy + 10)
}

const drawArtworkOnCanvas = () => {
  if (!ctx.value || !canvasRef.value) return
  const canvas = canvasRef.value
  
  // Clear first
  ctx.value.fillStyle = '#ffffff'
  ctx.value.fillRect(0, 0, canvas.width, canvas.height)
  
  if (selectedArtwork.value) {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const canvasRatio = canvas.width / canvas.height
      const imgRatio = img.width / img.height
      let drawWidth, drawHeight, offsetX, offsetY
      
      if (imgRatio > canvasRatio) {
        drawWidth = canvas.width
        drawHeight = canvas.width / imgRatio
        offsetX = 0
        offsetY = (canvas.height - drawHeight) / 2
      } else {
        drawHeight = canvas.height
        drawWidth = canvas.height * imgRatio
        offsetX = (canvas.width - drawWidth) / 2
        offsetY = 0
      }
      
      ctx.value.drawImage(img, offsetX, offsetY, drawWidth, drawHeight)
    }
    img.src = selectedArtwork.value.imagen_url
  } else {
    drawDefaultStarburst()
  }
}

const getMousePos = (event) => {
  const canvas = canvasRef.value
  const rect = canvas.getBoundingClientRect()
  
  let clientX = event.clientX
  let clientY = event.clientY
  
  if (event.touches && event.touches.length > 0) {
    clientX = event.touches[0].clientX
    clientY = event.touches[0].clientY
  }
  
  return {
    x: ((clientX - rect.left) / rect.width) * canvas.width,
    y: ((clientY - rect.top) / rect.height) * canvas.height
  }
}

const startDrawing = (event) => {
  drawing.value = true
  const pos = getMousePos(event)
  ctx.value.beginPath()
  ctx.value.moveTo(pos.x, pos.y)
  draw(event)
}

const draw = (event) => {
  if (!drawing.value || !ctx.value) return
  event.preventDefault()
  const pos = getMousePos(event)
  
  ctx.value.lineCap = 'round'
  ctx.value.lineJoin = 'round'
  
  if (activeTool.value === 'eraser') {
    ctx.value.strokeStyle = '#ffffff'
    ctx.value.lineWidth = 20
  } else if (activeTool.value === 'pencil') {
    ctx.value.strokeStyle = brushColor.value
    ctx.value.lineWidth = 1
  } else {
    ctx.value.strokeStyle = brushColor.value
    ctx.value.lineWidth = brushSize.value
  }
  
  ctx.value.lineTo(pos.x, pos.y)
  ctx.value.stroke()
}

const stopDrawing = () => {
  drawing.value = false
}

// Eye pupils track cursor coordinate state
const mouseCoord = ref({ x: 0, y: 0 })
const updateMouseCoordinates = (e) => {
  mouseCoord.value = { x: e.clientX, y: e.clientY }
}

const eyeOffset = computed(() => {
  const smileyBox = document.querySelector('.smiley-box')
  if (!smileyBox) return { x: 0, y: 0 }
  const rect = smileyBox.getBoundingClientRect()
  const smileyCenterX = rect.left + rect.width / 2
  const smileyCenterY = rect.top + rect.height / 2
  
  const angle = Math.atan2(mouseCoord.value.y - smileyCenterY, mouseCoord.value.x - smileyCenterX)
  // Max move pupil 3px
  return {
    x: Math.cos(angle) * 3,
    y: Math.sin(angle) * 3
  }
})

watch(selectedArtwork, () => {
  drawArtworkOnCanvas()
})

onMounted(() => {
  fetchData()
  updateClock()
  setInterval(updateClock, 1000)
  window.addEventListener('mousemove', updateMouseCoordinates)
  
  if (currentTheme.value === 'y2k') {
    setTimeout(() => {
      initCanvas()
    }, 500)
  }
})

const currentTheme = ref(localStorage.getItem('artfolio_theme') || 'y2k')

const toggleTheme = () => {
  currentTheme.value = currentTheme.value === 'y2k' ? 'gothic' : 'y2k'
  localStorage.setItem('artfolio_theme', currentTheme.value)
  if (currentTheme.value === 'y2k') {
    setTimeout(() => {
      initCanvas()
    }, 100)
  }
}

watch(currentTheme, (newTheme) => {
  document.body.className = `theme-${newTheme}`
}, { immediate: true })

onUnmounted(() => {
  document.body.className = ''
})
</script>

<template>
  <div v-if="currentTheme === 'y2k'" class="desktop-wrapper classic-cursor">
    <!-- Gothic Mode Shortcut on Desktop -->
    <div class="desktop-icon gothic-switch-shortcut" @click="toggleTheme">
      <div class="shortcut-icon-wrapper">🏰</div>
      <div class="shortcut-label-wrapper">Gothic Mode.lnk</div>
    </div>

    <!-- Halftone Yellow Starburst Decoration in Background -->
    <div class="starburst-bg"></div>

    <!-- Cyber Stars -->
    <svg 
      v-for="star in cyberStars" 
      :key="star.id" 
      class="cyber-star" 
      viewBox="0 0 24 24" 
      :style="{ 
        top: star.y + 'px', 
        left: star.x + 'px', 
        width: star.size + 'px', 
        height: star.size + 'px', 
        fill: star.color,
        animationDuration: star.duration
      }"
    >
      <path d="M12 0l3 9 9 3-9 3-3 9-3-9-9-3 9-3z"/>
    </svg>

    <!-- Draggable Vinyl Stickers -->
    <div 
      v-for="sticker in stickers" 
      :key="sticker.id" 
      class="y2k-sticker"
      :class="sticker.colorClass"
      :style="{ 
        top: sticker.y + 'px', 
        left: sticker.x + 'px', 
        transform: `rotate(${sticker.rotation}deg)` 
      }"
      @mousedown="startDrag($event, 'sticker', sticker.id)"
      @touchstart="startDrag($event, 'sticker', sticker.id)"
    >
      {{ sticker.text }}
    </div>

    <!-- WINDOW 1: Top-Left Title WordArt Window (Draggable) -->
    <div 
      class="win95-window purple-border logo-window"
      :style="{ top: positions.wordart.y + 'px', left: positions.wordart.x + 'px' }"
    >
      <div class="win95-title-bar purple-title" @mousedown="startDrag($event, 'window', 'wordart')" @touchstart="startDrag($event, 'window', 'wordart')">
        <div class="win95-title-text">✨ logo.gif</div>
        <div class="win95-title-bar-controls" @mousedown.stop>
          <button class="win95-btn">_</button>
          <button class="win95-btn">X</button>
        </div>
      </div>
      <div class="logo-text-wrapper">
        <h1 class="logo-wordart-title">Esouth</h1>
      </div>
    </div>

    <!-- WINDOW 2: Top-Right Smiley Window (Draggable) -->
    <div 
      class="win95-window purple-border smiley-window"
      :style="{ top: positions.smiley.y + 'px', left: positions.smiley.x + 'px' }"
    >
      <div class="win95-title-bar purple-title" @mousedown="startDrag($event, 'window', 'smiley')" @touchstart="startDrag($event, 'window', 'smiley')">
        <div class="win95-title-text">🙂 smiley.ico</div>
        <div class="win95-title-bar-controls" @mousedown.stop>
          <button class="win95-btn">_</button>
          <button class="win95-btn">X</button>
        </div>
      </div>
      <div class="smiley-box">
        <svg viewBox="0 0 100 100" class="pixel-smiley">
          <!-- Yellow Circle -->
          <circle cx="50" cy="50" r="45" fill="#ffe600" stroke="#000000" stroke-width="4" />
          <!-- Left Eye outer -->
          <circle cx="35" cy="40" r="8" fill="#ffffff" stroke="#000000" stroke-width="3" />
          <!-- Left Pupil -->
          <circle :cx="35 + eyeOffset.x" :cy="40 + eyeOffset.y" r="4" fill="#000000" />
          <!-- Right Eye outer -->
          <circle cx="65" cy="40" r="8" fill="#ffffff" stroke="#000000" stroke-width="3" />
          <!-- Right Pupil -->
          <circle :cx="65 + eyeOffset.x" :cy="40 + eyeOffset.y" r="4" fill="#000000" />
          <!-- Smile -->
          <path d="M 30 62 Q 50 82 70 62" fill="none" stroke="#000000" stroke-width="5" stroke-linecap="round" />
        </svg>
      </div>
    </div>

    <!-- WINDOW 3: Bottom-Left Warning Window (Draggable) -->
    <div 
      class="win95-window purple-border warning-window"
      :style="{ top: positions.warning.y + 'px', left: positions.warning.x + 'px' }"
    >
      <div class="win95-title-bar purple-title" @mousedown="startDrag($event, 'window', 'warning')" @touchstart="startDrag($event, 'window', 'warning')">
        <div class="win95-title-text">⚠️ warning.sys</div>
        <div class="win95-title-bar-controls" @mousedown.stop>
          <button class="win95-btn">X</button>
        </div>
      </div>
      <div class="warning-box clickable" @click="showWarningPopup = true">
        <div class="warning-pixel-icon">⚠️</div>
        <div class="warning-message">HAZARD: retro vibes detected! Click here to scan.</div>
      </div>
    </div>

    <!-- WINDOW 4: Bottom-Right Year Window (Draggable) -->
    <div 
      class="win95-window purple-border year-window"
      :style="{ top: positions.year.y + 'px', left: positions.year.x + 'px' }"
    >
      <div class="win95-title-bar purple-title" @mousedown="startDrag($event, 'window', 'year')" @touchstart="startDrag($event, 'window', 'year')">
        <div class="win95-title-text">📅 date.exe</div>
        <div class="win95-title-bar-controls" @mousedown.stop>
          <button class="win95-btn">X</button>
        </div>
      </div>
      <div class="year-content">
        <div class="year-digits">2025</div>
      </div>
    </div>

    <!-- WELCOME DIALOG (Classic Mac OS style, Draggable) -->
    <div 
      v-if="showWelcome" 
      class="win95-window welcome-dialog"
      :style="{ top: positions.welcome.y + 'px', left: positions.welcome.x + 'px' }"
    >
      <div class="win95-title-bar" @mousedown="startDrag($event, 'window', 'welcome')" @touchstart="startDrag($event, 'window', 'welcome')">
        <div class="win95-title-text">💾 System Message</div>
        <div class="win95-title-bar-controls" @mousedown.stop>
          <button class="win95-btn" @click="showWelcome = false">X</button>
        </div>
      </div>
      <div class="welcome-body win95-window-content">
        <div class="welcome-header">
          <span class="welcome-alert-icon">🖳</span>
          <div class="welcome-title">Welcome to ArtFolio v1.0!</div>
        </div>
        <p class="welcome-text">
          Estás ingresando al archivo visual retro de Esouth. Puedes explorar la galería de arte en el monitor CRT, dibujar en la pantalla e interactuar con los elementos del escritorio.
        </p>
        <div class="welcome-buttons">
          <button class="win95-btn welcome-ok" @click="showWelcome = false">OK</button>
          <button class="win95-btn welcome-cancel" @click="showWelcome = false">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- EXTRA WARNING POPUP (CHAOTIC Y2K FUN) -->
    <div 
      v-if="showWarningPopup" 
      class="win95-window warning-popup"
      :style="{ top: positions.warningPopup.y + 'px', left: positions.warningPopup.x + 'px' }"
    >
      <div class="win95-title-bar" @mousedown="startDrag($event, 'window', 'warningPopup')" @touchstart="startDrag($event, 'window', 'warningPopup')">
        <div class="win95-title-text">⚠️ High Aesthetic Warning</div>
        <div class="win95-title-bar-controls" @mousedown.stop>
          <button class="win95-btn" @click="showWarningPopup = false">X</button>
        </div>
      </div>
      <div class="welcome-body win95-window-content">
        <p class="warning-popup-msg">
          Se ha superado el límite de nostalgia recomendado para tu navegador. ¿Deseas continuar?
        </p>
        <div class="welcome-buttons">
          <button class="win95-btn welcome-ok" @click="showWarningPopup = false">¡Sí!</button>
          <button class="win95-btn welcome-ok" @click="showWarningPopup = false">Obvio</button>
        </div>
      </div>
    </div>

    <!-- MAIN CENTER CRT MONITOR -->
    <div class="crt-monitor-container">
      <div class="crt-monitor win95-outset">
        <div class="crt-bezel">
          <!-- Glass Screen -->
          <div class="crt-screen" :class="{ 'power-off': !monitorPower }">
            
            <div v-if="monitorPower" class="desktop-screen">
              
              <!-- OS Navigation Header -->
              <div class="sys-bar">
                <div class="sys-title">💻 ArtFolio Explorer v1.0</div>
                <div class="sys-clock">{{ clockTime }}</div>
              </div>

              <!-- Desktop body containing Sidebar and MS Paint canvas -->
              <div class="desktop-body">
                
                <!-- Sidebar File Manager (Collections & Artworks list) -->
                <div class="desktop-sidebar win95-inset">
                  <div class="sidebar-section">
                    <div class="sidebar-header">📂 Colecciones</div>
                    <div class="sidebar-list">
                      <div 
                        class="list-item clickable" 
                        :class="{ active: activeCollectionId === null }" 
                        @click="setCollection(null)"
                      >
                        📁 Ver Todas.col
                      </div>
                      <div 
                        v-for="col in collections" 
                        :key="col.id" 
                        class="list-item clickable"
                        :class="{ active: activeCollectionId === col.id }"
                        @click="setCollection(col.id)"
                      >
                        📁 {{ col.nombre.substring(0, 16) }}.col
                      </div>
                    </div>
                  </div>
                  
                  <div class="sidebar-divider"></div>

                  <div class="sidebar-section files-section">
                    <div class="sidebar-header">🖼️ Obras ({{ filteredArtworks.length }})</div>
                    
                    <!-- Search inside files -->
                    <div class="sidebar-search">
                      <input 
                        type="text" 
                        v-model="searchQuery" 
                        placeholder="Buscar..." 
                        class="win95-inset search-textbox"
                      />
                    </div>
                    
                    <div class="sidebar-list scrollable-files">
                      <div v-if="loading" class="sidebar-loader">
                        Cargando...
                      </div>
                      <div v-else-if="filteredArtworks.length === 0" class="sidebar-empty">
                        Sin archivos
                      </div>
                      <div 
                        v-else
                        v-for="art in filteredArtworks" 
                        :key="art.id" 
                        class="list-item file-item clickable"
                        :class="{ active: selectedArtwork?.id === art.id }"
                        @click="selectArtwork(art)"
                      >
                        📄 {{ art.titulo.substring(0, 18) }}.bmp
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Main Paint Canvas Workspace -->
                <div class="desktop-workspace">
                  <div class="win95-window paint-app win95-outset">
                    <div class="win95-title-bar">
                      <div class="win95-title-text">🎨 {{ selectedArtwork ? selectedArtwork.titulo + '.bmp' : 'untitled' }} - Paint</div>
                      <div class="win95-title-bar-controls">
                        <button class="win95-btn">_</button>
                        <button class="win95-btn" @click="clearPaintArea">X</button>
                      </div>
                    </div>
                    
                    <!-- MS Paint menus -->
                    <div class="paint-menu">
                      <span>Archivo</span>
                      <span>Edición</span>
                      <span>Ver</span>
                      <span>Imagen</span>
                      <span>Colores</span>
                      <span class="active-artwork-status" v-if="selectedArtwork">
                        [{{ selectedArtwork.estado }}]
                      </span>
                    </div>

                    <!-- Paint Workspace: Tool rack and Drawing canvas -->
                    <div class="paint-body">
                      <!-- Paint tools rack -->
                      <div class="paint-toolbar win95-outset">
                        <button 
                          v-for="tool in ['pencil', 'brush', 'eraser']" 
                          :key="tool" 
                          class="win95-btn tool-btn" 
                          :class="{ active: activeTool === tool }" 
                          @click="activeTool = tool"
                          :title="tool.toUpperCase()"
                        >
                          <span v-if="tool === 'pencil'">✏️</span>
                          <span v-else-if="tool === 'brush'">🖌️</span>
                          <span v-else-if="tool === 'eraser'">🧽</span>
                        </button>
                        
                        <div class="brush-size-select">
                          <label>Size</label>
                          <select v-model="brushSize" class="win95-inset size-select">
                            <option :value="1">1px</option>
                            <option :value="2">2px</option>
                            <option :value="4">4px</option>
                            <option :value="8">8px</option>
                            <option :value="12">12px</option>
                          </select>
                        </div>
                      </div>

                      <!-- Canvas viewport -->
                      <div class="paint-canvas-wrapper win95-inset">
                        <canvas 
                          ref="canvasRef" 
                          class="paint-canvas"
                          @mousedown="startDrawing" 
                          @mousemove="draw" 
                          @mouseup="stopDrawing" 
                          @mouseleave="stopDrawing"
                          @touchstart="startDrawing"
                          @touchmove="draw"
                          @touchend="stopDrawing"
                        ></canvas>
                      </div>
                    </div>

                    <!-- Paint colors palette at bottom -->
                    <div class="paint-palette win95-outset">
                      <div class="current-color win95-inset" :style="{ backgroundColor: brushColor }"></div>
                      <div class="palette-colors win95-inset">
                        <div 
                          v-for="color in [
                            '#000000', '#ffffff', '#808080', '#c0c0c0', 
                            '#ff0000', '#ffff00', '#00ff00', '#00ffff', 
                            '#0000ff', '#ff00ff', '#800080', '#008080',
                            '#ff00aa', '#ffe600', '#0c35fc', '#800020'
                          ]" 
                          :key="color" 
                          class="palette-color-box clickable" 
                          :style="{ backgroundColor: color }" 
                          @click="brushColor = color"
                        ></div>
                      </div>
                      <button class="win95-btn clear-btn" @click="clearPaintArea">Clear</button>
                    </div>
                  </div>
                </div>

              </div>

              <!-- Desktop Taskbar -->
              <div class="desktop-taskbar win95-outset">
                <div class="start-btn-container">
                  <button class="win95-btn start-btn" :class="{ active: showStartMenu }" @click="toggleStartMenu">
                    <span class="start-icon">🏁</span> Start
                  </button>
                  
                  <!-- Start Menu Popup -->
                  <div v-if="showStartMenu" class="win95-window start-menu">
                    <div class="start-menu-sidebar">
                      <div class="sidebar-text">ArtFolio 95</div>
                    </div>
                    <div class="start-menu-items">
                      <router-link to="/login" class="start-menu-item">
                        <span class="item-icon">🔒</span> Acceso Artista (Admin)
                      </router-link>
                      <div class="start-menu-separator"></div>
                      <a href="#" class="start-menu-item" @click.prevent="clearPaintArea(); showStartMenu = false">
                        <span class="item-icon">🗑️</span> Nuevo Lienzo
                      </a>
                      <a href="https://github.com" target="_blank" class="start-menu-item">
                        <span class="item-icon">🌐</span> Netscape Navigator
                      </a>
                    </div>
                  </div>
                </div>

                <div class="active-windows-list">
                  <button class="win95-btn tray-theme-btn" @click="toggleTheme">🏰 Gothic Mode</button>
                  <div class="task-tab win95-inset">🎨 untitled - Paint</div>
                </div>
              </div>

            </div>
          </div>
        </div>

        <!-- Bezel Controls -->
        <div class="crt-controls">
          <div class="brand-text">A E S T H E T I C</div>
          <div class="bezel-dials">
            <div class="dial"></div>
            <div class="dial"></div>
            <div class="dial"></div>
          </div>
          <div class="power-btn-group">
            <div class="power-led" :class="{ 'led-on': monitorPower }"></div>
            <button class="power-switch win95-btn" @click="toggleMonitorPower"></button>
          </div>
        </div>
      </div>
    </div>

    <!-- WINDOW 5: Floating Draggable TextEdit Window (Art details) -->
    <div 
      v-if="selectedArtwork"
      class="win95-window purple-border textedit-window"
      :style="{ top: positions.textedit.y + 'px', left: positions.textedit.x + 'px' }"
    >
      <div class="win95-title-bar purple-title" @mousedown="startDrag($event, 'window', 'textedit')" @touchstart="startDrag($event, 'window', 'textedit')">
        <div class="win95-title-text">📝 Info: {{ selectedArtwork.titulo }}.txt</div>
        <div class="win95-title-bar-controls" @mousedown.stop>
          <button class="win95-btn" @click="selectedArtwork = null">X</button>
        </div>
      </div>
      <div class="textedit-body win95-window-content">
        <div class="notepad-header">
          File Edit Search Help
        </div>
        <textarea class="notepad-textarea win95-inset" readonly :value="`TITULO: ${selectedArtwork.titulo}
TECNICA: ${selectedArtwork.tecnica}
DIMENSIONES: ${selectedArtwork.dimensiones}
AÑO: ${selectedArtwork.ano}
ESTADO: ${selectedArtwork.estado}
PRECIO: ${selectedArtwork.precio ? '$' + parseFloat(selectedArtwork.precio).toLocaleString('en-US', { minimumFractionDigits: 2 }) + ' USD' : 'N/A'}

DESCRIPCION:
Obra visual catalogada en el portafolio ArtFolio.`"></textarea>
        
        <div class="notepad-actions" v-if="selectedArtwork.estado === 'Disponible'">
          <a :href="getWhatsAppLink(selectedArtwork)" target="_blank" class="win95-btn acquire-btn">
            💬 Consultar Adquisición
          </a>
        </div>
      </div>
    </div>

    <!-- Floating Marquee Text at very bottom -->
    <div class="desktop-marquee win95-outset">
      <marquee scrollamount="4">
        ☄️ ARTFOLIO v1.0 — BIENVENIDO AL FUTURO ☄️ EXPLORA EL CATÁLOGO Y DIBUJA DIRECTAMENTE SOBRE LAS OBRAS DE ARTE ☄️ ESTILO RETRO WEBCORE Y2K ☄️
      </marquee>
    </div>
  </div>
  <div v-else class="artfolio-app">
    <!-- Cybersigil Background Grid & Details -->
    <div class="cybersigil-grid"></div>
    
    <!-- Top Sigil Border Ornament -->
    <div class="top-sigil-ornament">
      <svg viewBox="0 0 1000 40" class="sigil-line" preserveAspectRatio="none">
        <path d="M 0 20 L 400 20 L 420 10 L 450 30 L 460 15 L 480 25 L 500 0 L 520 25 L 540 15 L 550 30 L 580 10 L 600 20 L 1000 20" fill="none" stroke="#c5a059" stroke-width="1.5" />
        <circle cx="500" cy="0" r="4" fill="#c5a059" />
      </svg>
    </div>

    <!-- Header Section -->
    <header class="header">
      <button @click="toggleTheme" class="admin-portal-link y2k-toggle-link" style="right: auto; left: 20px;">⚡ Switch to Y2K Desktop</button>
      <div class="sigil-icon-left"></div>
      <div class="title-container">
        <h1 class="logo-text">ArtFolio</h1>
        <p class="subtitle">CMS de Portafolio Visual y Registro de Obras</p>
      </div>
      <div class="sigil-icon-right"></div>
      
      <!-- Artist Portal Link -->
      <router-link :to="{ path: '/login', query: { theme: 'gothic' } }" class="admin-portal-link">
        <span class="lock-icon">🔑</span> Acceso Artista
      </router-link>
    </header>

    <!-- Navigation & Filters -->
    <nav class="filters-nav">
      <div class="navigation-sigil-lines">
        <div class="sigil-line-half left"></div>
        <span class="navigation-title">Colecciones</span>
        <div class="sigil-line-half right"></div>
      </div>
      
      <div class="filter-buttons">
        <button 
          class="btn-filter" 
          :class="{ active: activeCollectionId === null }" 
          @click="setCollection(null)"
        >
          Ver Todas
        </button>
        <button 
          v-for="collection in collections" 
          :key="collection.id" 
          class="btn-filter"
          :class="{ active: activeCollectionId === collection.id }"
          @click="setCollection(collection.id)"
        >
          {{ collection.nombre }}
        </button>
      </div>
    </nav>

    <!-- Main Content Grid -->
    <main class="gallery-container">
      <div v-if="loading" class="loader-container">
        <div class="sigil-spinner"></div>
        <p class="loader-text">Cargando Portafolio...</p>
      </div>

      <div v-else-if="filteredArtworks.length === 0" class="empty-state">
        <p>No se encontraron obras registradas en esta selecci├│n.</p>
      </div>

      <!-- Masonry Layout -->
      <div v-else class="masonry-grid">
        <article 
          v-for="artwork in filteredArtworks" 
          :key="artwork.id" 
          class="artwork-card"
        >
          <!-- Cybersigil Corner Details -->
          <div class="card-sigil-corner top-left"></div>
          <div class="card-sigil-corner top-right"></div>
          <div class="card-sigil-corner bottom-left"></div>
          <div class="card-sigil-corner bottom-right"></div>

          <!-- Image Wrapper with Native Lazy Loading -->
          <div class="artwork-image-wrapper">
            <img 
              :src="artwork.imagen_url" 
              :alt="artwork.titulo" 
              class="artwork-image" 
              loading="lazy"
            />
            
            <!-- State Tag Overlay -->
            <div 
              class="status-tag" 
              :class="artwork.estado.toLowerCase().replace(' ', '-').normalize('NFD').replace(/[\u0300-\u036f]/g, '')"
            >
              {{ artwork.estado }}
            </div>
          </div>

          <!-- Artwork Information -->
          <div class="artwork-info">
            <h2 class="artwork-title">{{ artwork.titulo }}</h2>
            <div class="artwork-meta">
              <span class="meta-item tecnica">{{ artwork.tecnica }}</span>
              <span class="meta-item dimensiones">{{ artwork.dimensiones }}</span>
              <span class="meta-item ano">{{ artwork.ano }}</span>
            </div>
            <div class="artwork-footer" v-if="artwork.precio">
              <div class="footer-line"></div>
              <span class="artwork-price">${{ parseFloat(artwork.precio).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }} USD</span>
            </div>
          </div>
        </article>
      </div>
    </main>

    <!-- Bottom Footer Decor -->
    <footer class="footer">
      <div class="bottom-sigil-ornament">
        <svg viewBox="0 0 1000 40" class="sigil-line" preserveAspectRatio="none">
          <path d="M 0 20 L 400 20 L 420 30 L 450 10 L 460 25 L 480 15 L 500 40 L 520 15 L 540 25 L 550 10 L 580 30 L 600 20 L 1000 20" fill="none" stroke="#c5a059" stroke-width="1.5" />
          <circle cx="500" cy="40" r="4" fill="#c5a059" />
        </svg>
      </div>
      <p class="copyright">┬⌐ 2026 ArtFolio. Dise├▒ado en el claroscuro del arte anal├│gico y digital.</p>
    </footer>
  </div>
</template>

<style scoped>
/* Desktop Layout Grid */
.desktop-wrapper {
  position: relative;
  width: 100vw;
  min-height: 100vh;
  overflow: hidden;
  box-sizing: border-box;
  padding: 20px;
}

/* Background starburst clip path styling */
.starburst-bg {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 800px;
  height: 800px;
  background-color: var(--y2k-yellow);
  clip-path: polygon(
    50% 0%, 54% 33%, 80% 12%, 67% 43%, 100% 50%, 67% 57%, 80% 88%, 54% 67%, 
    50% 100%, 46% 67%, 20% 88%, 33% 57%, 0% 50%, 33% 43%, 20% 12%, 46% 33%
  );
  filter: drop-shadow(0 0 40px rgba(255, 230, 0, 0.5));
  z-index: 1;
  pointer-events: none;
}

/* Draggable Windows custom styling sizes */
.logo-window {
  width: 250px;
  z-index: 90;
}

.logo-text-wrapper {
  padding: 15px;
  text-align: center;
  background-color: #000000;
  border: 2px inset var(--win-grey);
}

.logo-wordart-title {
  font-family: 'Cinzel', serif;
  font-size: 2.8rem;
  font-weight: bold;
  font-style: italic;
  margin: 0;
  background: linear-gradient(135deg, #0c35fc, #ff00ff, #ffff00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(2px 2px 0px #ffffff) drop-shadow(0 0 10px rgba(255, 0, 255, 0.8));
  line-height: 1.1;
  letter-spacing: -1px;
}

.smiley-window {
  width: 140px;
  z-index: 90;
}

.smiley-box {
  padding: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #ffffff;
}

.pixel-smiley {
  width: 90px;
  height: 90px;
}

.warning-window {
  width: 280px;
  z-index: 90;
}

.warning-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background-color: #ffffff;
}

.warning-pixel-icon {
  font-size: 2.2rem;
}

.warning-message {
  font-size: 11px;
  font-family: 'Tahoma', sans-serif;
  color: #000000;
}

.year-window {
  width: 160px;
  z-index: 90;
}

.year-content {
  padding: 10px;
  background-color: #000000;
  text-align: center;
  border: 2px inset var(--win-grey);
}

.year-digits {
  font-family: 'Cinzel', serif;
  font-size: 3.2rem;
  font-weight: 900;
  color: var(--y2k-cyan);
  text-shadow: 2px 2px 0px var(--y2k-magenta), 0 0 12px var(--y2k-cyan);
  line-height: 1;
}

/* Welcome Dialog OS Styling */
.welcome-dialog {
  width: 420px;
  z-index: 100;
}

.welcome-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 12px;
}

.welcome-alert-icon {
  font-size: 2.5rem;
}

.welcome-title {
  font-size: 14px;
  font-weight: bold;
}

.welcome-text {
  font-size: 12px;
  line-height: 1.4;
  margin-bottom: 15px;
}

.welcome-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.welcome-ok, .welcome-cancel {
  padding: 4px 15px;
  font-size: 12px;
  min-width: 75px;
}

.warning-popup {
  width: 320px;
  z-index: 110;
}

.warning-popup-msg {
  font-size: 12px;
  line-height: 1.3;
  margin-bottom: 15px;
}

/* CRT Monitor styles */
.crt-monitor-container {
  display: flex;
  justify-content: center;
  width: 100%;
  position: relative;
  z-index: 10;
  pointer-events: none; /* Let background elements remain clickable except monitor itself */
}

.crt-monitor {
  pointer-events: auto; /* Re-enable pointer events for the monitor */
  width: 780px;
  background-color: #dfdfdf;
  border-top: 3px solid #ffffff;
  border-left: 3px solid #ffffff;
  border-right: 3px solid #777777;
  border-bottom: 3px solid #777777;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.6);
  margin-top: 100px;
  margin-bottom: 50px;
  box-sizing: border-box;
}

.crt-bezel {
  background-color: #c0c0c0;
  border-top: 3px solid #777777;
  border-left: 3px solid #777777;
  border-right: 3px solid #ffffff;
  border-bottom: 3px solid #ffffff;
  padding: 10px;
  border-radius: 4px;
}

.crt-screen {
  background-color: #000000;
  border-radius: 12px;
  border: 10px solid #1a1a1a;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 0 30px #000000;
  aspect-ratio: 4 / 3;
}

/* CRT Scanline phosphor glow overlay */
.crt-screen::after {
  content: " ";
  display: block;
  position: absolute;
  top: 0; left: 0; bottom: 0; right: 0;
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.2) 50%), 
              linear-gradient(90deg, rgba(255, 0, 0, 0.05), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.05));
  background-size: 100% 3px, 6px 100%;
  z-index: 99;
  pointer-events: none;
  opacity: 0.95;
}

/* Monitor power state */
.crt-screen.power-off {
  background-color: #0d0e15 !important;
}
.crt-screen.power-off::after {
  display: none;
}
.crt-screen.power-off .desktop-screen {
  display: none;
}

/* OS UI Inside Monitor */
.desktop-screen {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #008080; /* Classic Win95 Teal desktop */
  font-family: 'Tahoma', 'MS Sans Serif', sans-serif;
  font-size: 11px;
}

.sys-bar {
  background-color: #000080;
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  padding: 2px 6px;
  font-weight: bold;
}

.desktop-body {
  flex-grow: 1;
  display: flex;
  overflow: hidden;
  padding: 6px;
  gap: 6px;
}

/* Sidebar structure inside monitor */
.desktop-sidebar {
  width: 160px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 4px;
  box-sizing: border-box;
}

.sidebar-section {
  display: flex;
  flex-direction: column;
}

.files-section {
  flex-grow: 1;
  overflow: hidden;
}

.sidebar-header {
  background-color: #e0e0e0;
  padding: 3px 6px;
  font-weight: bold;
  border-bottom: 1px solid #808080;
  margin-bottom: 4px;
}

.sidebar-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 100px;
  overflow-y: auto;
}

.scrollable-files {
  flex-grow: 1;
  max-height: none !important;
  overflow-y: auto;
}

.sidebar-search {
  padding: 3px 0;
}

.search-textbox {
  width: 100%;
  box-sizing: border-box;
  padding: 2px 4px;
  font-size: 10px;
  outline: none;
}

.sidebar-divider {
  height: 2px;
  background-color: #808080;
  margin: 6px 0;
}

.list-item {
  padding: 3px 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  user-select: none;
}

.list-item.active {
  background-color: #000080;
  color: #ffffff;
}

.file-item {
  padding-left: 12px;
}

.sidebar-loader, .sidebar-empty {
  padding: 6px;
  color: #555555;
  font-style: italic;
}

/* Paint Workspace styling */
.desktop-workspace {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.paint-app {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.paint-menu {
  background-color: var(--win-grey);
  border-bottom: 1px solid var(--win-border-dark);
  padding: 3px 8px;
  display: flex;
  gap: 12px;
  user-select: none;
  font-weight: normal;
}

.paint-menu span {
  cursor: pointer;
}

.active-artwork-status {
  margin-left: auto;
  color: #800000;
  font-weight: bold;
}

.paint-body {
  flex-grow: 1;
  display: flex;
  padding: 4px;
  gap: 4px;
  overflow: hidden;
}

.paint-toolbar {
  width: 48px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 4px;
  align-items: center;
}

.tool-btn {
  width: 32px;
  height: 32px;
  font-size: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.tool-btn.active {
  background-color: #e0e0e0;
  border-top: 1.5px solid var(--win-border-dark);
  border-left: 1.5px solid var(--win-border-dark);
  border-right: 1.5px solid var(--win-border-light);
  border-bottom: 1.5px solid var(--win-border-light);
  box-shadow: none;
  padding: 1px 0 0 1px;
}

.brush-size-select {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 9px;
  gap: 2px;
}

.size-select {
  font-size: 9px;
  background-color: #ffffff;
  padding: 1px;
  outline: none;
}

.paint-canvas-wrapper {
  flex-grow: 1;
  background-color: #808080;
  padding: 3px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.paint-canvas {
  background-color: #ffffff;
  max-width: 100%;
  max-height: 100%;
  display: block;
  cursor: crosshair;
}

.paint-palette {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  gap: 8px;
}

.current-color {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.palette-colors {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 2px;
  padding: 2px;
  background-color: #ffffff;
  flex-grow: 1;
}

.palette-color-box {
  width: 12px;
  height: 12px;
  border: 1px solid #777777;
}

.clear-btn {
  padding: 2px 10px;
  font-size: 11px;
}

/* Taskbar styling */
.desktop-taskbar {
  height: 28px;
  display: flex;
  align-items: center;
  padding: 2px 4px;
  gap: 6px;
  box-sizing: border-box;
}

.start-btn-container {
  position: relative;
}

.start-btn {
  font-weight: bold;
  padding: 2px 10px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.start-btn.active {
  border-top: 1.5px solid var(--win-border-dark);
  border-left: 1.5px solid var(--win-border-dark);
  border-right: 1.5px solid var(--win-border-light);
  border-bottom: 1.5px solid var(--win-border-light);
  box-shadow: none;
  padding: 3px 9px 1px 11px;
}

.start-icon {
  font-size: 12px;
}

.start-menu {
  position: absolute;
  bottom: 26px;
  left: 0;
  width: 180px;
  z-index: 999;
  display: flex;
}

.start-menu-sidebar {
  background-color: #000080;
  width: 24px;
  display: flex;
  align-items: flex-end;
  padding: 6px;
}

.sidebar-text {
  color: #ffffff;
  font-weight: bold;
  transform: rotate(-90deg);
  transform-origin: 0 0;
  white-space: nowrap;
  font-size: 14px;
  margin-bottom: 15px;
}

.start-menu-items {
  flex-grow: 1;
  background-color: var(--win-grey);
  display: flex;
  flex-direction: column;
  padding: 2px;
}

.start-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  color: #000000;
  text-decoration: none;
  font-size: 11px;
}

.start-menu-item:hover {
  background-color: #000080;
  color: #ffffff;
}

.start-menu-separator {
  height: 1px;
  background-color: #808080;
  margin: 3px 0;
}

.active-windows-list {
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-tab {
  background-color: #dfdfdf;
  padding: 3px 12px;
  font-weight: bold;
  border-top: 1.5px solid var(--win-border-dark);
  border-left: 1.5px solid var(--win-border-dark);
  border-right: 1.5px solid var(--win-border-light);
  border-bottom: 1.5px solid var(--win-border-light);
}

/* Monitor physical bezel dials and power button */
.crt-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding: 4px 10px;
}

.brand-text {
  font-family: monospace;
  font-size: 12px;
  font-weight: bold;
  letter-spacing: 4px;
  color: #555555;
}

.bezel-dials {
  display: flex;
  gap: 8px;
}

.dial {
  width: 10px;
  height: 10px;
  background-color: #888888;
  border-radius: 50%;
  border: 1px solid #555555;
}

.power-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.power-led {
  width: 6px;
  height: 6px;
  background-color: #4a1515;
  border-radius: 50%;
}

.power-led.led-on {
  background-color: #00ff00;
  box-shadow: 0 0 6px #00ff00;
}

.power-switch {
  width: 24px;
  height: 16px;
  background-color: #c0c0c0;
}

/* WINDOW 5: Floating Draggable TextEdit window styling */
.textedit-window {
  width: 320px;
  z-index: 100;
}

.notepad-header {
  font-size: 11px;
  padding: 3px 6px;
  border-bottom: 1px solid #808080;
  background-color: var(--win-grey);
  display: flex;
  gap: 12px;
  color: #000000;
  user-select: none;
}

.notepad-textarea {
  width: 100%;
  height: 180px;
  box-sizing: border-box;
  resize: none;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  padding: 8px;
  outline: none;
  border: 2px inset var(--win-grey);
  background-color: #ffffff;
  color: #000000;
}

.notepad-actions {
  margin-top: 8px;
}

.acquire-btn {
  display: block;
  text-align: center;
  text-decoration: none;
  padding: 6px 12px;
  font-weight: bold;
}

/* Bottom banner marquee styling */
.desktop-marquee {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 4px;
  font-family: 'VT323', monospace;
  font-size: 1.3rem;
  z-index: 9999;
}

.clickable {
  cursor: pointer;
}

/* Responsive fixes */
@media (max-width: 820px) {
  .starburst-bg {
    width: 450px;
    height: 450px;
  }
  .crt-monitor {
    width: 100%;
    margin-top: 160px;
  }
  .logo-window, .smiley-window, .warning-window, .year-window, .textedit-window {
    position: static !important;
    margin-bottom: 15px;
    width: 100% !important;
  }
  .desktop-wrapper {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }
}

/* Theme Switcher Styles */
.gothic-switch-shortcut {
  position: absolute;
  top: 120px;
  left: 20px;
  text-align: center;
  width: 80px;
  cursor: pointer;
  z-index: 90;
  transition: transform 0.2s;
}
.gothic-switch-shortcut:hover {
  transform: scale(1.05);
}
.gothic-switch-shortcut .shortcut-icon-wrapper {
  font-size: 32px;
  filter: drop-shadow(1px 1px 0px #000);
}
.gothic-switch-shortcut .shortcut-label-wrapper {
  font-size: 11px;
  color: #ffffff;
  background-color: #000000;
  padding: 2px 4px;
  border: 1px dotted #ffffff;
  margin-top: 4px;
  font-family: 'MS Sans Serif', 'Tahoma', sans-serif;
  word-break: break-all;
}
.tray-theme-btn {
  font-size: 11px;
  font-weight: bold;
  margin-left: 10px;
  background-color: var(--win-grey);
  border: 2px outset #ffffff;
  padding: 2px 6px;
  cursor: pointer;
  font-family: 'MS Sans Serif', 'Tahoma', sans-serif;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 22px;
  vertical-align: middle;
}
.tray-theme-btn:active {
  border-style: inset;
}
.y2k-toggle-link {
  font-weight: bold;
  border-color: #c5a059;
  color: #c5a059;
}
.y2k-toggle-link:hover {
  background: rgba(12, 53, 252, 0.2) !important;
  border-color: #0c35fc !important;
  color: #fff !important;
}

/* Scoped styles to isolate the components structure */
.artfolio-app {
  min-height: 100vh;
  position: relative;
  color: #f4f0e6;
  padding: 2rem 1.5rem;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-x: hidden;
  width: 100%;
}

/* Background overlay grid - Cybersigil vibe */
.cybersigil-grid {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at center, rgba(107, 29, 47, 0.05) 0%, transparent 80%),
              radial-gradient(circle at 10% 20%, rgba(20, 20, 18, 0.98) 0%, #0d0d0c 100%);
  background-size: cover;
  z-index: -2;
}

/* Header design */
.header {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  max-width: 1100px;
  margin-bottom: 2.5rem;
  position: relative;
  text-align: center;
}

.title-container {
  z-index: 1;
}

.logo-text {
  font-family: 'UnifrakturMaguntia', 'Cinzel', serif;
  font-size: 4.5rem;
  color: #c5a059;
  margin: 0;
  letter-spacing: 0.15em;
  text-shadow: 0 0 10px rgba(197, 160, 89, 0.2), 0 0 20px rgba(107, 29, 47, 0.3);
  line-height: 1.1;
}

.subtitle {
  font-family: 'Cinzel', serif;
  font-size: 0.95rem;
  color: #a39b8c;
  letter-spacing: 0.3em;
  margin-top: 0.5rem;
  text-transform: uppercase;
}

.admin-portal-link {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  color: #c5a059;
  text-decoration: none;
  font-family: 'Outfit', sans-serif;
  font-size: 0.85rem;
  font-weight: 400;
  letter-spacing: 0.1em;
  border: 1px solid rgba(197, 160, 89, 0.3);
  padding: 0.5rem 1rem;
  background: rgba(28, 27, 24, 0.6);
  transition: all 0.3s;
}

.admin-portal-link:hover {
  background: rgba(107, 29, 47, 0.25);
  border-color: #c5a059;
  box-shadow: 0 0 10px rgba(197, 160, 89, 0.2);
}

.lock-icon {
  margin-right: 4px;
}

/* Sigil Ornaments surrounding header */
.sigil-line {
  width: 100%;
  height: 40px;
  stroke-dasharray: 1000;
  animation: draw-line 2.5s ease-out forwards;
}

.top-sigil-ornament, .bottom-sigil-ornament {
  width: 100%;
  max-width: 1100px;
  margin-bottom: 1.5rem;
}

/* Filters & Navigation */
.filters-nav {
  width: 100%;
  max-width: 1100px;
  margin-bottom: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.navigation-sigil-lines {
  display: flex;
  align-items: center;
  width: 100%;
  margin-bottom: 1.5rem;
}

.sigil-line-half {
  flex-grow: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(197, 160, 89, 0.4), transparent);
  position: relative;
}

.sigil-line-half::before {
  content: '';
  position: absolute;
  top: -3px;
  width: 7px;
  height: 7px;
  border: 1px solid #c5a059;
  transform: rotate(45deg);
}

.sigil-line-half.left::before {
  right: 0;
}
.sigil-line-half.right::before {
  left: 0;
}

.navigation-title {
  font-family: 'Cinzel', serif;
  text-transform: uppercase;
  letter-spacing: 0.4em;
  color: #c5a059;
  font-size: 0.9rem;
  padding: 0 1.5rem;
}

.filter-buttons {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-filter {
  background: rgba(28, 27, 24, 0.6);
  border: 1px solid rgba(197, 160, 89, 0.25);
  color: #a39b8c;
  padding: 0.6rem 1.8rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.9rem;
  font-weight: 300;
  letter-spacing: 0.15em;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  text-transform: uppercase;
}

.btn-filter::before {
  content: '';
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  border: 1px solid transparent;
  pointer-events: none;
  transition: all 0.4s;
}

.btn-filter:hover {
  background: rgba(107, 29, 47, 0.15);
  border-color: #c5a059;
  color: #f4f0e6;
  box-shadow: 0 0 10px rgba(197, 160, 89, 0.15);
}

.btn-filter:hover::before {
  border-color: rgba(197, 160, 89, 0.1);
  transform: scale(1.02);
}

.btn-filter.active {
  background: rgba(107, 29, 47, 0.25);
  border-color: #c5a059;
  color: #c5a059;
  box-shadow: 0 0 15px rgba(107, 29, 47, 0.3);
  text-shadow: 0 0 5px rgba(197, 160, 89, 0.5);
}

/* Gallery & Masonry Grid */
.gallery-container {
  width: 100%;
  max-width: 1100px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.masonry-grid {
  column-count: 3;
  column-gap: 2rem;
  width: 100%;
}

@media (max-width: 992px) {
  .masonry-grid {
    column-count: 2;
    column-gap: 1.5rem;
  }
}

@media (max-width: 640px) {
  .masonry-grid {
    column-count: 1;
  }
}

/* Artwork Card design */
.artwork-card {
  break-inside: avoid;
  background: rgba(28, 27, 24, 0.7);
  border: 1px solid rgba(197, 160, 89, 0.15);
  margin-bottom: 2rem;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: visible;
  transition: all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.artwork-card:hover {
  transform: translateY(-8px);
  border-color: #c5a059;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7),
              0 0 15px rgba(197, 160, 89, 0.1);
}

/* Cybersigil Corner Ornaments on Cards */
.card-sigil-corner {
  position: absolute;
  width: 12px;
  height: 12px;
  border: 1.5px solid transparent;
  pointer-events: none;
  z-index: 10;
  transition: all 0.5s;
}

.artwork-card:hover .card-sigil-corner {
  border-color: #c5a059;
}

.card-sigil-corner.top-left {
  top: -3px;
  left: -3px;
  border-right: none;
  border-bottom: none;
}
.card-sigil-corner.top-right {
  top: -3px;
  right: -3px;
  border-left: none;
  border-bottom: none;
}
.card-sigil-corner.bottom-left {
  bottom: -3px;
  left: -3px;
  border-right: none;
  border-top: none;
}
.card-sigil-corner.bottom-right {
  bottom: -3px;
  right: -3px;
  border-left: none;
  border-top: none;
}

/* Image styling */
.artwork-image-wrapper {
  width: 100%;
  position: relative;
  overflow: hidden;
  background: #0d0d0c;
}

.artwork-image {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.8s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.artwork-card:hover .artwork-image {
  transform: scale(1.05);
}

/* Tags */
.status-tag {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.35rem 0.9rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  border-radius: 2px;
  z-index: 2;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
}

/* Status colors - styled high contrast dark academia */
.status-tag.disponible {
  background: rgba(46, 77, 53, 0.9);
  border: 1px solid #a3e635;
  color: #a3e635;
}

.status-tag.en-exhibicion {
  background: rgba(92, 68, 28, 0.9);
  border: 1px solid #fde047;
  color: #fde047;
}

.status-tag.vendida {
  background: rgba(107, 29, 47, 0.9);
  border: 1px solid #fda4af;
  color: #fda4af;
}

/* Card details styling */
.artwork-info {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.artwork-title {
  font-family: 'Cinzel', serif;
  font-size: 1.25rem;
  color: #f4f0e6;
  margin: 0 0 0.6rem 0;
  letter-spacing: 0.05em;
  line-height: 1.3;
}

.artwork-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.meta-item {
  font-family: 'Outfit', sans-serif;
  font-size: 0.8rem;
  font-weight: 300;
  color: #a39b8c;
}

.tecnica {
  font-style: italic;
}

/* Card footer separator & price */
.footer-line {
  height: 1px;
  background: linear-gradient(90deg, rgba(197, 160, 89, 0.3), transparent);
  margin: 0.8rem 0;
}

.artwork-price {
  font-family: 'Cinzel', serif;
  font-size: 1.05rem;
  color: #c5a059;
  font-weight: 700;
  letter-spacing: 0.05em;
}

/* Loader & Spinners */
.loader-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
}

.sigil-spinner {
  width: 50px;
  height: 50px;
  border: 2px solid rgba(197, 160, 89, 0.1);
  border-top: 2px solid #c5a059;
  border-bottom: 2px solid #c5a059;
  border-radius: 50%;
  animation: spin 2s linear infinite;
  margin-bottom: 1.5rem;
  position: relative;
}

.sigil-spinner::before {
  content: '';
  position: absolute;
  top: 5px;
  left: 5px;
  right: 5px;
  bottom: 5px;
  border: 1px solid transparent;
  border-left: 1.5px solid #800020;
  border-right: 1.5px solid #800020;
  border-radius: 50%;
  animation: spin-reverse 1.2s linear infinite;
}

.loader-text {
  font-family: 'Cinzel', serif;
  letter-spacing: 0.2em;
  color: #a39b8c;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  font-family: 'Outfit', sans-serif;
  color: #a39b8c;
  border: 1px dashed rgba(197, 160, 89, 0.2);
  background: rgba(28, 27, 24, 0.3);
}

/* Footer Section */
.footer {
  width: 100%;
  max-width: 1100px;
  margin-top: auto;
  padding-top: 4rem;
  padding-bottom: 1rem;
  text-align: center;
}

.copyright {
  font-family: 'Outfit', sans-serif;
  font-size: 0.75rem;
  font-weight: 300;
  color: #5c574f;
  letter-spacing: 0.1em;
}

/* Animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes spin-reverse {
  0% { transform: rotate(360deg); }
  100% { transform: rotate(0deg); }
}

@keyframes draw-line {
  0% { stroke-dashoffset: 1000; }
  100% { stroke-dashoffset: 0; }
}
</style>
