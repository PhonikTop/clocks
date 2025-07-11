import { ref } from 'vue'

export function useToasts() {
  const toasts = ref([])
  let idCounter = 0

  const addToast = (message, type = 'info', duration = 5000) => {
    const id = idCounter++
    const toast = {
      id,
      message,
      type,
      duration,
      timeoutId: null,
      remaining: duration,
      startTime: Date.now(),
    }

    toast.timeoutId = setTimeout(() => removeToast(id), duration)
    toasts.value.push(toast)
  }

  const removeToast = (id) => {
    const toast = toasts.value.find(t => t.id === id)
    if (toast) {
      clearTimeout(toast.timeoutId)
    }
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  const pauseToast = (id) => {
    const toast = toasts.value.find(t => t.id === id)
    if (!toast) return
    const elapsed = Date.now() - toast.startTime
    toast.remaining = toast.remaining - elapsed
    clearTimeout(toast.timeoutId)
  }

  const resumeToast = (id) => {
    const toast = toasts.value.find(t => t.id === id)
    if (!toast || toast.remaining <= 0) {
      removeToast(id)
      return
    }

    toast.startTime = Date.now()
    toast.timeoutId = setTimeout(() => removeToast(id), toast.remaining)
  }

  return {
    toasts,
    addToast,
    removeToast,
    pauseToast,
    resumeToast
  }
}
