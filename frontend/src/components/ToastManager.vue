<script setup lang="ts">
import { useToastStore } from "@/stores/toasts"

const toasts = useToastStore()

</script>

<template>
  <Teleport to="body">
    <div class="toast toast-end z-50">
      <div
        v-for="toast in toasts.toasts"
        :key="toast.id"
        :class="[
          'alert',
          toast.type === 'info' ? 'alert-info' : '',
          toast.type === 'success' ? 'alert-success' : '',
          toast.type === 'error' ? 'alert-error' : '',
          toast.type === 'warning' ? 'alert-warning' : '',
          'font-bold'
        ]"
        class="w-80 shadow-lg flex items-center justify-between"
        @mouseenter="toasts.pauseToast(toast.id)"
        @mouseleave="toasts.resumeToast(toast.id)"
      >
        <span>{{ toast.message }}</span>
        <button
          class="btn btn-sm btn-ghost ml-2"
          @click="toasts.removeToast(toast.id)"
        >
          ✕
        </button>
      </div>
    </div>
  </Teleport>
</template>