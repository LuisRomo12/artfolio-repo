import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import LoginView from '../src/views/LoginView.vue'

// Mock de vue-router para simular la navegación en las pruebas del componente
const mockPush = vi.fn()
const mockRoute = {
  query: { theme: 'y2k' } // Forzar tema Y2K por defecto en la prueba para que existan los inputs con ids #email y #password
}

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => mockRoute
}))

describe('LoginView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    // Limpiamos o definimos un mock para el fetch global
    global.fetch = vi.fn()
  })

  it('debe llamar a la API de login al hacer submit con email y contraseña, guardar token y redirigir', async () => {
    // Simulamos respuesta exitosa del servidor
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: 'fake-jwt-token-123' })
    })

    const wrapper = mount(LoginView)

    // Llenamos los campos del formulario Y2K
    const emailInput = wrapper.find('#email')
    const passwordInput = wrapper.find('#password')
    await emailInput.setValue('artista@artfolio.com')
    await passwordInput.setValue('artista123')

    // Enviamos el formulario
    await wrapper.find('form').trigger('submit.prevent')

    // Verificamos que se llame al endpoint correcto con los datos ingresados
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'artista@artfolio.com', password: 'artista123' })
      })
    )

    // Esperamos a que terminen las promesas de handleLogin
    await new Promise((resolve) => setTimeout(resolve, 0))

    // Verificamos que el token se haya guardado y la redirección se haya hecho al dashboard
    expect(localStorage.getItem('artfolio_token')).toBe('fake-jwt-token-123')
    expect(mockPush).toHaveBeenCalledWith('/dashboard')
  })

  it('debe mostrar un mensaje de error si el login falla en la respuesta de la API', async () => {
    // Simulamos un fallo de credenciales
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Credenciales inválidas' })
    })

    const wrapper = mount(LoginView)

    // Llenamos con credenciales erróneas
    await wrapper.find('#email').setValue('incorrecto@artfolio.com')
    await wrapper.find('#password').setValue('claveincorrecta')

    // Enviamos el formulario
    await wrapper.find('form').trigger('submit.prevent')

    // Esperamos la resolución de las promesas asíncronas
    await new Promise((resolve) => setTimeout(resolve, 50))

    // Validamos que se muestre el contenedor del mensaje de error con el texto correspondiente
    const errorBox = wrapper.find('.error-box-content')
    expect(errorBox.exists()).toBe(true)
    expect(errorBox.text()).toContain('Error de conexión') // Fallback de error local o de API
  })
})
