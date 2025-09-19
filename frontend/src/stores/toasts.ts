import { defineStore } from "pinia"

type ToastType = "info" | "success" | "warning" | "error"

export interface Toast {
  id: number
  message: string
  type: ToastType
  duration: number
  timeoutId: ReturnType<typeof setTimeout> | null
  remaining: number
  startTime: number
}

export const useToastStore = defineStore("toasts", {
  state: () => ({
    toasts: [] as Toast[],
    idCounter: 0,
  }),

  actions: {
    addToast(message: string, type: ToastType = "info", duration = 5000) {
      const id = this.idCounter++
      const toast: Toast = {
        id,
        message,
        type,
        duration,
        timeoutId: null,
        remaining: duration,
        startTime: Date.now(),
      }

      toast.timeoutId = setTimeout(() => this.removeToast(id), duration)
      this.toasts.push(toast)
    },

    removeToast(id: number) {
      const toast = this.toasts.find((t) => t.id === id)
      if (toast && toast.timeoutId) {
        clearTimeout(toast.timeoutId)
      }
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },

    pauseToast(id: number) {
      const toast = this.toasts.find((t) => t.id === id)
      if (!toast) return

      const elapsed = Date.now() - toast.startTime
      toast.remaining = toast.remaining - elapsed
      if (toast.timeoutId) {
        clearTimeout(toast.timeoutId)
        toast.timeoutId = null
      }
    },

    resumeToast(id: number) {
      const toast = this.toasts.find((t) => t.id === id)
      if (!toast || toast.remaining <= 0) {
        this.removeToast(id)
        return
      }

      toast.startTime = Date.now()
      toast.timeoutId = setTimeout(() => this.removeToast(id), toast.remaining)
    },
  },
})
