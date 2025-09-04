import { ref, Ref } from "vue";

type ToastType = "info" | "success" | "warning" | "error";

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
  duration: number;
  timeoutId: ReturnType<typeof setTimeout> | null;
  remaining: number;
  startTime: number;
}

export function useToasts() {
  const toasts: Ref<Toast[]> = ref([]);
  let idCounter = 0;

  const addToast = (
    message: string,
    type: ToastType = "info",
    duration = 5000
  ): void => {
    const id = idCounter++;
    const toast: Toast = {
      id,
      message,
      type,
      duration,
      timeoutId: null,
      remaining: duration,
      startTime: Date.now(),
    };

    toast.timeoutId = setTimeout(() => removeToast(id), duration);
    toasts.value.push(toast);
  };

  const removeToast = (id: number): void => {
    const toast = toasts.value.find((t) => t.id === id);
    if (toast && toast.timeoutId) {
      clearTimeout(toast.timeoutId);
    }
    toasts.value = toasts.value.filter((t) => t.id !== id);
  };

  const pauseToast = (id: number): void => {
    const toast = toasts.value.find((t) => t.id === id);
    if (!toast) return;

    const elapsed = Date.now() - toast.startTime;
    toast.remaining = toast.remaining - elapsed;
    if (toast.timeoutId) {
      clearTimeout(toast.timeoutId);
      toast.timeoutId = null;
    }
  };

  const resumeToast = (id: number): void => {
    const toast = toasts.value.find((t) => t.id === id);
    if (!toast || toast.remaining <= 0) {
      removeToast(id);
      return;
    }

    toast.startTime = Date.now();
    toast.timeoutId = setTimeout(() => removeToast(id), toast.remaining);
  };

  return {
    toasts,
    addToast,
    removeToast,
    pauseToast,
    resumeToast,
  };
}
