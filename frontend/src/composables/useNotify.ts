import { useToastStore } from "@/stores/toasts"

type ToastType = "info" | "success" | "warning" | "error";


export function useNotify() {
  const toastStore = useToastStore()

  const notify = (message: string, type: ToastType = 'info', duration = 5000) => {
    toastStore.addToast(message, type, duration)
  }

  return {
    notify,
    success: (msg: string, duration = 4000) => notify(msg, 'success', duration),
    error: (msg: string, duration = 5000) => notify(msg, 'error', duration),
    warning: (msg: string, duration = 5000) => notify(msg, 'warning', duration),
    info: (msg: string, duration = 4000) => notify(msg, 'info', duration),
  }
}
