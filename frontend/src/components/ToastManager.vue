<script setup>
import { inject } from 'vue'

const toast = inject('toast')
if (!toast) throw new Error('Toast not provided!')

const { toasts, pauseToast, resumeToast, removeToast } = toast
</script>

<template>
  <Teleport to="body">
    <div class="toast toast-end z-50">
      <div
        v-for="toast in toasts"
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
        @mouseenter="pauseToast(toast.id)"
        @mouseleave="resumeToast(toast.id)"
      >
        <span>{{ toast.message }}</span>
        <button class="btn btn-sm btn-ghost ml-2" @click="removeToast(toast.id)">✕</button>
      </div>
    </div>
  </Teleport>
</template>