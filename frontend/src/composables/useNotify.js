import { inject } from 'vue'

export function useNotify() {
  const toast = inject('toast')
  if (!toast) {
    throw new Error('Toast not provided')
  }

  const notify = (message, type = 'info', duration = 5000) => {
    toast.addToast(message, type, duration)
  }

  return {
    notify,
    success: (msg, duration = 4000) => notify(msg, 'success', duration),
    error: (msg, duration = 5000) => notify(msg, 'error', duration),
    warning: (msg, duration = 5000) => notify(msg, 'warning', duration),
    info: (msg, duration = 4000) => notify(msg, 'info', duration),
  }
}
