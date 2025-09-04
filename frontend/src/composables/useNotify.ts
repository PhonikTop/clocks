import { inject } from 'vue'
import { useToasts } from './useToasts'

export type ToastContext = ReturnType<typeof useToasts>;
type ToastType = "info" | "success" | "warning" | "error";


export function useNotify() {
  const toast = inject<ToastContext>("toast");
  if (!toast) {
    throw new Error('Toast not provided')
  }

  const notify = (message: string, type: ToastType = 'info', duration = 5000) => {
    toast.addToast(message, type, duration)
  }

  return {
    notify,
    success: (msg: string, duration = 4000) => notify(msg, 'success', duration),
    error: (msg: string, duration = 5000) => notify(msg, 'error', duration),
    warning: (msg: string, duration = 5000) => notify(msg, 'warning', duration),
    info: (msg: string, duration = 4000) => notify(msg, 'info', duration),
  }
}
