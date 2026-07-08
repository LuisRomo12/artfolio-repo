import { describe, it, expect, beforeEach, vi } from 'vitest'
import router from '../src/router/index.js'

describe('Router Navigation Guards', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('debe bloquear el acceso a /dashboard e ir a /login si no hay token', async () => {
    // Iniciamos en la raíz
    await router.push('/')
    expect(router.currentRoute.value.path).toBe('/')

    // Intentamos ir a /dashboard
    await router.push('/dashboard')

    // Debe redirigirnos a la pantalla de Login
    expect(router.currentRoute.value.name).toBe('Login')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('debe permitir acceder a /dashboard si el token existe en localStorage', async () => {
    // Simulamos que el usuario ya se logueó
    localStorage.setItem('artfolio_token', 'token-valido-123')

    // Intentamos ir a /dashboard
    await router.push('/dashboard')

    // El acceso debe ser exitoso
    expect(router.currentRoute.value.name).toBe('Dashboard')
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })
})
