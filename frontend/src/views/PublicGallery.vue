<script setup>
import { ref, onMounted, computed } from 'vue'

// API base URL
const API_URL = 'http://localhost:8000'

// State variables
const artworks = ref([])
const collections = ref([])
const activeCollectionId = ref(null)
const loading = ref(true)

// Fallback Mock Data for Demo/Staging
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
  }
}

// Select collection to filter
const setCollection = (id) => {
  activeCollectionId.value = id
}

// Computed property to filter artworks reactively
const filteredArtworks = computed(() => {
  if (activeCollectionId.value === null) {
    return artworks.value
  }
  return artworks.value.filter(artwork => artwork.coleccion_id === activeCollectionId.value)
})

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="artfolio-app">
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
      <div class="sigil-icon-left"></div>
      <div class="title-container">
        <h1 class="logo-text">ArtFolio</h1>
        <p class="subtitle">CMS de Portafolio Visual y Registro de Obras</p>
      </div>
      <div class="sigil-icon-right"></div>
      
      <!-- Artist Portal Link -->
      <router-link to="/login" class="admin-portal-link">
        <span class="lock-icon">🔒</span> Acceso Artista
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
        <p>No se encontraron obras registradas en esta selección.</p>
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
      <p class="copyright">© 2026 ArtFolio. Diseñado en el claroscuro del arte analógico y digital.</p>
    </footer>
  </div>
</template>

<style scoped>
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
