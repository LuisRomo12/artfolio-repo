<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const router = useRouter()

// State variables
const artworks = ref([])
const collections = ref([])
const loading = ref(true)
const token = ref(localStorage.getItem('artfolio_token'))

// Form modal state
const showModal = ref(false)
const submitting = ref(false)
const formError = ref('')
const isEditing = ref(false)
const editingArtworkId = ref(null)

// Image upload state
const uploadingImage = ref(false)
const uploadError = ref('')

// New/Edit Artwork Form State
const newArtwork = ref({
  titulo: '',
  tecnica: '',
  dimensiones: '',
  ano: new Date().getFullYear(),
  precio: null,
  imagen_url: '',
  estado: 'Disponible',
  coleccion_id: null
})

// Tab selection
const activeTab = ref('artworks') // 'artworks' or 'collections'

// Collection form modal state
const showCollectionModal = ref(false)
const submittingCollection = ref(false)
const collectionFormError = ref('')
const isEditingCollection = ref(false)
const editingCollectionId = ref(null)

const newCollection = ref({
  nombre: '',
  descripcion: ''
})

// Mock fallback data
const mockCollections = [
  { id: 1, nombre: "Mitologías Perdidas" },
  { id: 2, nombre: "Anatomía de la Melancolía" }
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
    dimensions: "40 x 30 cm",
    ano: 2023,
    precio: 350.00,
    imagen_url: "https://images.unsplash.com/photo-1579783928621-7a13d66a62d1?q=80&w=600&auto=format&fit=crop",
    estado: "En exhibición",
    coleccion_id: 2,
    created_at: "2026-06-02T12:00:00Z"
  }
]

// Fetch inventory data
const fetchInventory = async () => {
  loading.value = true
  try {
    const headers = {
      'Authorization': `Bearer ${token.value}`
    }
    
    // Fetch artworks
    const artworksRes = await fetch(`${API_URL}/artworks/`, { headers })
    if (artworksRes.ok) {
      artworks.value = await artworksRes.json()
    } else {
      throw new Error()
    }
    
    // Fetch collections
    const collectionsRes = await fetch(`${API_URL}/collections/`, { headers })
    if (collectionsRes.ok) {
      collections.value = await collectionsRes.json()
    } else {
      throw new Error()
    }
  } catch (err) {
    console.warn("Backend connection failed. Displaying mockup inventory.", err)
    artworks.value = mockArtworks
    collections.value = mockCollections
  } finally {
    loading.value = false
  }
}

// Upload file to backend
const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  uploadingImage.value = true
  uploadError.value = ''

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${API_URL}/artworks/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token.value}`
      },
      body: formData
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Error al subir la imagen')
    }

    const data = await response.json()
    newArtwork.value.imagen_url = data.imagen_url
  } catch (err) {
    console.error("Upload error:", err)
    uploadError.value = err.message || 'Error al subir la imagen'
  } finally {
    uploadingImage.value = false
  }
}

// Add new artwork API call
const handleAddArtwork = async () => {
  submitting.value = true
  formError.value = ''
  
  // Format price if empty
  const payload = {
    ...newArtwork.value,
    precio: newArtwork.value.precio ? parseFloat(newArtwork.value.precio) : null,
    coleccion_id: newArtwork.value.coleccion_id ? parseInt(newArtwork.value.coleccion_id) : null
  }
  
  try {
    const response = await fetch(`${API_URL}/artworks/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify(payload)
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      // Handle details list if returned from FastAPI
      const errDetail = Array.isArray(data.detail) ? data.detail[0].msg : data.detail
      throw new Error(errDetail || 'Error al guardar la obra')
    }
    
    // Success: add to reactive list
    artworks.value.unshift(data)
    closeFormModal()
  } catch (err) {
    console.error("Save error, falling back to mock addition:", err)
    // Fallback Mock save
    const mockCreated = {
      ...payload,
      id: Math.floor(Math.random() * 1000) + 200,
      created_at: new Date().toISOString()
    }
    artworks.value.unshift(mockCreated)
    closeFormModal()
  } finally {
    submitting.value = false
  }
}

// Update artwork API call
const handleEditArtwork = async () => {
  submitting.value = true
  formError.value = ''
  
  const payload = {
    ...newArtwork.value,
    precio: newArtwork.value.precio ? parseFloat(newArtwork.value.precio) : null,
    coleccion_id: newArtwork.value.coleccion_id ? parseInt(newArtwork.value.coleccion_id) : null
  }
  
  try {
    const response = await fetch(`${API_URL}/artworks/${editingArtworkId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify(payload)
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      const errDetail = Array.isArray(data.detail) ? data.detail[0].msg : data.detail
      throw new Error(errDetail || 'Error al actualizar la obra')
    }
    
    // Success: update reactive list
    const index = artworks.value.findIndex(a => a.id === editingArtworkId.value)
    if (index !== -1) {
      artworks.value[index] = data
    }
    closeFormModal()
  } catch (err) {
    console.error("Update error, applying locally (mock mode):", err)
    const index = artworks.value.findIndex(a => a.id === editingArtworkId.value)
    if (index !== -1) {
      artworks.value[index] = {
        ...artworks.value[index],
        ...payload
      }
    }
    closeFormModal()
  } finally {
    submitting.value = false
  }
}

const handleSubmit = async () => {
  if (isEditing.value) {
    await handleEditArtwork()
  } else {
    await handleAddArtwork()
  }
}

// Collection CRUD functions
const openCollectionModal = (collection = null) => {
  showCollectionModal.value = true
  collectionFormError.value = ''
  if (collection) {
    isEditingCollection.value = true
    editingCollectionId.value = collection.id
    newCollection.value = {
      nombre: collection.nombre,
      descripcion: collection.descripcion || ''
    }
  } else {
    isEditingCollection.value = false
    editingCollectionId.value = null
    newCollection.value = {
      nombre: '',
      descripcion: ''
    }
  }
}

const closeCollectionModal = () => {
  showCollectionModal.value = false
  isEditingCollection.value = false
  editingCollectionId.value = null
}

const handleAddCollection = async () => {
  submittingCollection.value = true
  collectionFormError.value = ''
  try {
    const response = await fetch(`${API_URL}/collections/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify(newCollection.value)
    })
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || 'Error al guardar la colección')
    }
    collections.value.push(data)
    closeCollectionModal()
  } catch (err) {
    console.error("Save collection error, falling back to mock:", err)
    const mockCreated = {
      ...newCollection.value,
      id: Math.floor(Math.random() * 1000) + 50,
      created_at: new Date().toISOString()
    }
    collections.value.push(mockCreated)
    closeCollectionModal()
  } finally {
    submittingCollection.value = false
  }
}

const handleEditCollection = async () => {
  submittingCollection.value = true
  collectionFormError.value = ''
  try {
    const response = await fetch(`${API_URL}/collections/${editingCollectionId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify(newCollection.value)
    })
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || 'Error al actualizar la colección')
    }
    const index = collections.value.findIndex(c => c.id === editingCollectionId.value)
    if (index !== -1) {
      collections.value[index] = data
    }
    closeCollectionModal()
  } catch (err) {
    console.error("Update collection error, applying locally (mock mode):", err)
    const index = collections.value.findIndex(c => c.id === editingCollectionId.value)
    if (index !== -1) {
      collections.value[index] = {
        ...collections.value[index],
        ...newCollection.value
      }
    }
    closeCollectionModal()
  } finally {
    submittingCollection.value = false
  }
}

const handleSubmitCollection = async () => {
  if (isEditingCollection.value) {
    await handleEditCollection()
  } else {
    await handleAddCollection()
  }
}

const handleDeleteCollection = async (id) => {
  if (!confirm('¿Seguro que deseas eliminar esta colección? Las obras asociadas quedarán sin colección.')) return
  try {
    const response = await fetch(`${API_URL}/collections/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token.value}`
      }
    })
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Error al eliminar la colección')
    }
    collections.value = collections.value.filter(c => c.id !== id)
    artworks.value.forEach(artwork => {
      if (artwork.coleccion_id === id) {
        artwork.coleccion_id = null
      }
    })
  } catch (err) {
    console.error("Delete collection failed, applying locally (mock mode):", err)
    collections.value = collections.value.filter(c => c.id !== id)
    artworks.value.forEach(artwork => {
      if (artwork.coleccion_id === id) {
        artwork.coleccion_id = null
      }
    })
  }
}

// Delete artwork API call
const handleDeleteArtwork = async (id) => {
  if (!confirm('¿Seguro que deseas eliminar esta obra del inventario?')) return
  
  try {
    const response = await fetch(`${API_URL}/artworks/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token.value}`
      }
    })
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Error al eliminar')
    }
    
    // Remove from local list
    artworks.value = artworks.value.filter(artwork => artwork.id !== id)
  } catch (err) {
    console.error("Delete failed, applying locally (mock mode):", err)
    artworks.value = artworks.value.filter(artwork => artwork.id !== id)
  }
}

// Helpers
const openFormModal = (artwork = null) => {
  showModal.value = true
  formError.value = ''
  uploadError.value = ''
  
  if (artwork) {
    isEditing.value = true
    editingArtworkId.value = artwork.id
    newArtwork.value = {
      titulo: artwork.titulo,
      tecnica: artwork.tecnica,
      dimensiones: artwork.dimensiones,
      ano: artwork.ano,
      precio: artwork.precio,
      imagen_url: artwork.imagen_url,
      estado: artwork.estado,
      coleccion_id: artwork.coleccion_id
    }
  } else {
    isEditing.value = false
    editingArtworkId.value = null
    newArtwork.value = {
      titulo: '',
      tecnica: '',
      dimensiones: '',
      ano: new Date().getFullYear(),
      precio: null,
      imagen_url: '',
      estado: 'Disponible',
      coleccion_id: collections.value.length > 0 ? collections.value[0].id : null
    }
  }
}

const closeFormModal = () => {
  showModal.value = false
  isEditing.value = false
  editingArtworkId.value = null
}

const handleLogout = () => {
  localStorage.removeItem('artfolio_token')
  router.push('/login')
}

// Mount hook - check JWT
onMounted(() => {
  if (!token.value) {
    router.push('/login')
    return
  }
  fetchInventory()
})
</script>

<template>
  <div class="dashboard-wrapper">
    <div class="cybersigil-bg"></div>
    
    <!-- Top Sigil Border -->
    <div class="top-sigil-ornament">
      <svg viewBox="0 0 1000 30" class="sigil-line" preserveAspectRatio="none">
        <path d="M 0 15 L 450 15 L 470 5 L 490 25 L 500 0 L 510 25 L 530 5 L 550 15 L 1000 15" fill="none" stroke="#c5a059" stroke-width="1.2" />
      </svg>
    </div>

    <div class="dashboard-container">
      <!-- Admin Header -->
      <header class="dashboard-header">
        <div class="brand">
          <h1 class="logo">ArtFolio</h1>
          <span class="badge">Panel de Inventario</span>
        </div>
        
        <div class="header-actions">
          <router-link to="/" class="btn-secondary">Ver Portal</router-link>
          <button @click="handleLogout" class="btn-logout">Cerrar Sesión</button>
        </div>
      </header>

      <!-- Tabs Navigation -->
      <nav class="admin-tabs">
        <button class="tab-btn" :class="{ active: activeTab === 'artworks' }" @click="activeTab = 'artworks'">
          Inventario de Obras
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'collections' }" @click="activeTab = 'collections'">
          Gestión de Colecciones
        </button>
      </nav>

      <!-- Main Panel -->
      <main class="panel">
        <div v-if="loading" class="loader-container">
          <div class="spinner"></div>
          <p>Cargando catálogo privado...</p>
        </div>

        <div v-else>
          <!-- Artwork Table Tab -->
          <div v-if="activeTab === 'artworks'" class="table-responsive">
            <table class="inventory-table">
              <thead>
                <tr>
                  <th>Imagen</th>
                  <th>Título</th>
                  <th>Técnica</th>
                  <th>Dimensiones</th>
                  <th>Año</th>
                  <th>Precio</th>
                  <th>Colección</th>
                  <th>Estado</th>
                  <th class="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="artworks.length === 0">
                  <td colspan="9" class="empty-table">No hay obras en el inventario actual.</td>
                </tr>
                <tr v-for="artwork in artworks" :key="artwork.id">
                  <td class="td-image">
                    <img :src="artwork.imagen_url" :alt="artwork.titulo" class="thumbnail" />
                  </td>
                  <td class="td-title">{{ artwork.titulo }}</td>
                  <td>{{ artwork.tecnica }}</td>
                  <td>{{ artwork.dimensiones }}</td>
                  <td>{{ artwork.ano }}</td>
                  <td class="price">
                    <span v-if="artwork.precio">${{ parseFloat(artwork.precio).toLocaleString('en-US', { minimumFractionDigits: 2 }) }} USD</span>
                    <span v-else class="no-price">—</span>
                  </td>
                  <td>
                    <span class="collection-name">
                      {{ collections.find(c => c.id === artwork.coleccion_id)?.nombre || 'Sin Colección' }}
                    </span>
                  </td>
                  <td>
                    <span class="status-tag" :class="artwork.estado.toLowerCase().replace(' ', '-').normalize('NFD').replace(/[\u0300-\u036f]/g, '')">
                      {{ artwork.estado }}
                    </span>
                  </td>
                  <td class="text-right">
                    <button @click="openFormModal(artwork)" class="btn-edit" title="Editar obra" style="margin-right: 0.5rem;">
                      Editar
                    </button>
                    <button @click="handleDeleteArtwork(artwork.id)" class="btn-delete" title="Eliminar obra">
                      Eliminar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Collection Table Tab -->
          <div v-else-if="activeTab === 'collections'" class="table-responsive">
            <table class="inventory-table">
              <thead>
                <tr>
                  <th>Nombre de la Colección</th>
                  <th>Descripción</th>
                  <th>Fecha de Creación</th>
                  <th class="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="collections.length === 0">
                  <td colspan="4" class="empty-table">No hay colecciones registradas.</td>
                </tr>
                <tr v-for="col in collections" :key="col.id">
                  <td class="td-title">{{ col.nombre }}</td>
                  <td>{{ col.descripcion || 'Sin descripción' }}</td>
                  <td>{{ new Date(col.created_at || new Date()).toLocaleDateString() }}</td>
                  <td class="text-right">
                    <button @click="openCollectionModal(col)" class="btn-edit" title="Editar colección" style="margin-right: 0.5rem;">
                      Editar
                    </button>
                    <button @click="handleDeleteCollection(col.id)" class="btn-delete" title="Eliminar colección">
                      Eliminar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>

      <!-- Floating Action Button (FAB) -->
      <button class="fab" @click="activeTab === 'artworks' ? openFormModal() : openCollectionModal()" :title="activeTab === 'artworks' ? 'Agregar obra nueva' : 'Agregar colección nueva'">
        <span class="plus-icon">+</span>
      </button>

      <!-- Create/Edit Artwork Modal -->
      <div v-if="showModal" class="modal-overlay" @click.self="closeFormModal">
        <div class="modal-card">
          <!-- Cybersigil Corner Details -->
          <div class="modal-sigil top-left"></div>
          <div class="modal-sigil top-right"></div>
          <div class="modal-sigil bottom-left"></div>
          <div class="modal-sigil bottom-right"></div>
          
          <header class="modal-header">
            <h3>{{ isEditing ? 'Editar Obra' : 'Registrar Nueva Obra' }}</h3>
            <button @click="closeFormModal" class="btn-close-modal">✕</button>
          </header>

          <form @submit.prevent="handleSubmit" class="modal-form">
            <div v-if="formError" class="form-error-alert">{{ formError }}</div>

            <div class="form-row">
              <div class="form-group flex-2">
                <label>Título de la Obra *</label>
                <input type="text" v-model="newArtwork.titulo" required placeholder="Ej. El Lamento de Ícaro" class="modal-input" />
              </div>
              <div class="form-group flex-1">
                <label>Año de Creación *</label>
                <input type="number" v-model="newArtwork.ano" required placeholder="Ej. 2026" class="modal-input" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Técnica *</label>
                <input type="text" v-model="newArtwork.tecnica" required placeholder="Ej. Óleo sobre lienzo" class="modal-input" />
              </div>
              <div class="form-group">
                <label>Dimensiones *</label>
                <input type="text" v-model="newArtwork.dimensiones" required placeholder="Ej. 120 x 90 cm" class="modal-input" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Precio (Opcional USD)</label>
                <input type="number" step="0.01" v-model="newArtwork.precio" placeholder="Ej. 1200.00" class="modal-input" />
              </div>
              <div class="form-group">
                <label>Colección Relacionada</label>
                <select v-model="newArtwork.coleccion_id" class="modal-input select">
                  <option :value="null">Ninguna colección</option>
                  <option v-for="col in collections" :key="col.id" :value="col.id">
                    {{ col.nombre }}
                  </option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Estado de Disponibilidad *</label>
              <div class="radio-group">
                <label class="radio-label">
                  <input type="radio" v-model="newArtwork.estado" value="Disponible" />
                  <span>Disponible</span>
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="newArtwork.estado" value="Vendida" />
                  <span>Vendida</span>
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="newArtwork.estado" value="En exhibición" />
                  <span>En exhibición</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Imagen de la Obra *</label>
              <div class="upload-container">
                <input type="file" @change="handleFileUpload" accept="image/*" class="file-input-hidden" id="file-upload" />
                <label for="file-upload" class="btn-upload-label">
                  <span>📁 Seleccionar Archivo</span>
                </label>
                <input type="url" v-model="newArtwork.imagen_url" required placeholder="O pega una URL: https://..." class="modal-input file-url-input" />
              </div>
              <div v-if="uploadingImage" class="upload-loader">Subiendo imagen...</div>
              <div v-if="uploadError" class="upload-error-text">{{ uploadError }}</div>
              <div v-if="newArtwork.imagen_url" class="image-preview-container">
                <img :src="newArtwork.imagen_url" class="preview-img" />
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" @click="closeFormModal" class="btn-cancel">Cancelar</button>
              <button type="submit" class="btn-save" :disabled="submitting || uploadingImage">
                <span v-if="submitting">Guardando...</span>
                <span v-else-if="isEditing">Guardar Cambios</span>
                <span v-else>Guardar Obra</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Create/Edit Collection Modal -->
      <div v-if="showCollectionModal" class="modal-overlay" @click.self="closeCollectionModal">
        <div class="modal-card">
          <!-- Cybersigil Corner Details -->
          <div class="modal-sigil top-left"></div>
          <div class="modal-sigil top-right"></div>
          <div class="modal-sigil bottom-left"></div>
          <div class="modal-sigil bottom-right"></div>
          
          <header class="modal-header">
            <h3>{{ isEditingCollection ? 'Editar Colección' : 'Crear Nueva Colección' }}</h3>
            <button @click="closeCollectionModal" class="btn-close-modal">✕</button>
          </header>

          <form @submit.prevent="handleSubmitCollection" class="modal-form">
            <div v-if="collectionFormError" class="form-error-alert">{{ collectionFormError }}</div>

            <div class="form-group">
              <label>Nombre de la Colección *</label>
              <input type="text" v-model="newCollection.nombre" required placeholder="Ej. Mitologías Perdidas" class="modal-input" />
            </div>

            <div class="form-group">
              <label>Descripción (Opcional)</label>
              <textarea v-model="newCollection.descripcion" rows="4" placeholder="Describe el concepto de esta colección..." class="modal-input textarea"></textarea>
            </div>

            <div class="modal-footer">
              <button type="button" @click="closeCollectionModal" class="btn-cancel">Cancelar</button>
              <button type="submit" class="btn-save" :disabled="submittingCollection">
                <span v-if="submittingCollection">Guardando...</span>
                <span v-else-if="isEditingCollection">Guardar Cambios</span>
                <span v-else>Crear Colección</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-wrapper {
  min-height: 100vh;
  color: #f4f0e6;
  width: 100%;
  padding: 1.5rem;
  box-sizing: border-box;
  position: relative;
}

.cybersigil-bg {
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at center, rgba(107, 29, 47, 0.05) 0%, transparent 80%),
              #0d0d0c;
  z-index: -2;
}

.top-sigil-ornament {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto 1.5rem auto;
}

.sigil-line {
  width: 100%;
  height: 30px;
}

.dashboard-container {
  max-width: 1100px;
  margin: 0 auto;
  position: relative;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(197, 160, 89, 0.2);
  padding-bottom: 1.5rem;
  margin-bottom: 2rem;
}

.brand {
  display: flex;
  align-items: baseline;
  gap: 1rem;
}

.logo {
  font-family: 'Cinzel', serif;
  font-size: 2.2rem;
  color: #c5a059;
  letter-spacing: 0.1em;
}

.badge {
  font-family: 'Outfit', sans-serif;
  font-size: 0.8rem;
  color: #a39b8c;
  border: 1px solid rgba(197, 160, 89, 0.3);
  padding: 0.2rem 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  background: rgba(28, 27, 24, 0.6);
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-secondary {
  color: #a39b8c;
  text-decoration: none;
  border: 1px solid rgba(163, 155, 140, 0.3);
  padding: 0.5rem 1.2rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.85rem;
  transition: all 0.3s;
  background: transparent;
}

.btn-secondary:hover {
  border-color: #f4f0e6;
  color: #f4f0e6;
}

.btn-logout {
  background: #6b1d2f;
  border: 1px solid rgba(197, 160, 89, 0.3);
  color: #f4f0e6;
  padding: 0.5rem 1.2rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-logout:hover {
  background: #800020;
  border-color: #c5a059;
}

/* Panel & Table design */
.panel {
  background: rgba(28, 27, 24, 0.8);
  border: 1px solid rgba(197, 160, 89, 0.15);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  padding: 1rem;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
}

.inventory-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Outfit', sans-serif;
  font-size: 0.9rem;
  text-align: left;
}

.inventory-table th {
  border-bottom: 2px solid rgba(197, 160, 89, 0.3);
  padding: 1rem;
  color: #c5a059;
  font-family: 'Cinzel', serif;
  font-size: 0.8rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.inventory-table td {
  padding: 1rem;
  border-bottom: 1px solid rgba(197, 160, 89, 0.1);
  vertical-align: middle;
  color: #e3dec3;
}

.inventory-table tr:hover td {
  background: rgba(107, 29, 47, 0.05);
}

.empty-table {
  text-align: center;
  padding: 3rem !important;
  color: #a39b8c;
}

.td-image {
  width: 60px;
}

.thumbnail {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border: 1px solid rgba(197, 160, 89, 0.2);
}

.td-title {
  font-family: 'Cinzel', serif;
  color: #f4f0e6;
  font-weight: 700;
}

.price {
  font-weight: 600;
}

.no-price {
  color: #5c574f;
}

.collection-name {
  color: #a39b8c;
}

/* Status tag */
.status-tag {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  border-radius: 1px;
}

.status-tag.disponible {
  background: rgba(46, 77, 53, 0.2);
  border: 1px solid rgba(163, 230, 53, 0.5);
  color: #a3e635;
}

.status-tag.en-exhibicion {
  background: rgba(92, 68, 28, 0.2);
  border: 1px solid rgba(253, 224, 71, 0.5);
  color: #fde047;
}

.status-tag.vendida {
  background: rgba(107, 29, 47, 0.2);
  border: 1px solid rgba(253, 164, 175, 0.5);
  color: #fda4af;
}

.text-right {
  text-align: right;
}

.btn-delete {
  background: transparent;
  color: #fda4af;
  border: 1px solid rgba(253, 164, 175, 0.3);
  padding: 0.35rem 0.8rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-delete:hover {
  background: #6b1d2f;
  border-color: #fda4af;
}

/* Floating Action Button (FAB) */
.fab {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #6b1d2f;
  border: 2px solid #c5a059;
  color: #f4f0e6;
  font-size: 2rem;
  cursor: pointer;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  z-index: 99;
}

.fab:hover {
  transform: scale(1.1) rotate(90deg);
  background: #800020;
  box-shadow: 0 8px 25px rgba(197, 160, 89, 0.3);
}

.plus-icon {
  margin-top: -3px;
}

/* Modal form style */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(13, 13, 12, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
  padding: 1.5rem;
  box-sizing: border-box;
}

.modal-card {
  width: 100%;
  max-width: 600px;
  background: #1c1b18;
  border: 1px solid #c5a059;
  padding: 2.5rem 2rem;
  box-sizing: border-box;
  position: relative;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
}

/* Modal Y2K Sigils */
.modal-sigil {
  position: absolute;
  width: 15px;
  height: 15px;
  border: 1px solid #c5a059;
}

.modal-sigil.top-left { top: -3px; left: -3px; border-right: none; border-bottom: none; }
.modal-sigil.top-right { top: -3px; right: -3px; border-left: none; border-bottom: none; }
.modal-sigil.bottom-left { bottom: -3px; left: -3px; border-right: none; border-top: none; }
.modal-sigil.bottom-right { bottom: -3px; right: -3px; border-left: none; border-top: none; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(197, 160, 89, 0.2);
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  font-family: 'Cinzel', serif;
  color: #c5a059;
  font-size: 1.3rem;
  letter-spacing: 0.05em;
}

.btn-close-modal {
  background: transparent;
  border: none;
  color: #a39b8c;
  font-size: 1.2rem;
  cursor: pointer;
  transition: color 0.3s;
}

.btn-close-modal:hover {
  color: #f4f0e6;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-error-alert {
  background: rgba(107, 29, 47, 0.2);
  border: 1px solid #6b1d2f;
  color: #fda4af;
  padding: 0.6rem;
  font-size: 0.8rem;
}

.form-row {
  display: flex;
  gap: 1.5rem;
}

@media (max-width: 480px) {
  .form-row {
    flex-direction: column;
    gap: 1.25rem;
  }
}

.flex-1 { flex: 1; }
.flex-2 { flex: 2; }

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.form-group label {
  font-family: 'Cinzel', serif;
  font-size: 0.75rem;
  color: #c5a059;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.modal-input {
  background: #0d0d0c;
  border: 1px solid rgba(197, 160, 89, 0.3);
  color: #f4f0e6;
  padding: 0.65rem 0.8rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.9rem;
  transition: border-color 0.3s;
}

.modal-input:focus {
  outline: none;
  border-color: #c5a059;
  box-shadow: 0 0 5px rgba(197, 160, 89, 0.1);
}

.modal-input.select {
  cursor: pointer;
}

.modal-input option {
  background: #1c1b18;
  color: #f4f0e6;
}

.radio-group {
  display: flex;
  gap: 2rem;
  margin-top: 0.25rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.radio-label input {
  accent-color: #c5a059;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid rgba(197, 160, 89, 0.2);
  padding-top: 1.5rem;
  margin-top: 1rem;
}

.btn-cancel {
  background: transparent;
  color: #a39b8c;
  border: 1px solid rgba(163, 155, 140, 0.3);
  padding: 0.6rem 1.5rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel:hover {
  border-color: #f4f0e6;
  color: #f4f0e6;
}

.btn-save {
  background: #6b1d2f;
  border: 1px solid #c5a059;
  color: #f4f0e6;
  padding: 0.6rem 1.8rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-save:hover:not(:disabled) {
  background: #800020;
  box-shadow: 0 0 10px rgba(197, 160, 89, 0.3);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Loader anim */
.loader-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  gap: 1rem;
  color: #a39b8c;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 2px solid rgba(197, 160, 89, 0.2);
  border-top: 2px solid #c5a059;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn-edit {
  background: transparent;
  color: #c5a059;
  border: 1px solid rgba(197, 160, 89, 0.3);
  padding: 0.35rem 0.8rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-edit:hover {
  background: rgba(197, 160, 89, 0.15);
  border-color: #c5a059;
}

/* Upload component styling */
.upload-container {
  display: flex;
  gap: 1rem;
  align-items: center;
  width: 100%;
}

.file-input-hidden {
  display: none;
}

.btn-upload-label {
  background: #1c1b18;
  border: 1px solid rgba(197, 160, 89, 0.4);
  color: #c5a059;
  padding: 0.65rem 1.2rem;
  font-size: 0.85rem;
  cursor: pointer;
  white-space: nowrap;
  font-family: 'Outfit', sans-serif;
  transition: all 0.3s;
}

.btn-upload-label:hover {
  background: rgba(197, 160, 89, 0.1);
  border-color: #c5a059;
}

.file-url-input {
  flex-grow: 1;
}

.upload-loader {
  font-size: 0.8rem;
  color: #c5a059;
  font-style: italic;
  margin-top: 0.25rem;
}

.upload-error-text {
  font-size: 0.8rem;
  color: #fda4af;
  margin-top: 0.25rem;
}

.image-preview-container {
  margin-top: 0.75rem;
  width: 120px;
  height: 120px;
  border: 1px solid rgba(197, 160, 89, 0.2);
  padding: 3px;
  background: #0d0d0c;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Tabs Navigation */
.admin-tabs {
  display: flex;
  gap: 1.5rem;
  max-width: 1100px;
  margin: 0 auto 1.5rem auto;
  border-bottom: 1px solid rgba(197, 160, 89, 0.15);
  padding-bottom: 0.25rem;
}

.tab-btn {
  background: transparent;
  border: none;
  color: #a39b8c;
  padding: 0.5rem 1rem;
  font-family: 'Cinzel', serif;
  font-size: 0.9rem;
  letter-spacing: 0.05em;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: #c5a059;
}

.tab-btn.active {
  color: #f4f0e6;
  font-weight: bold;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -0.35rem;
  left: 0;
  width: 100%;
  height: 2px;
  background: #c5a059;
  box-shadow: 0 0 8px #c5a059;
}

/* Textarea input style */
.modal-input.textarea {
  resize: vertical;
  font-family: 'Outfit', sans-serif;
  line-height: 1.5;
}
</style>
