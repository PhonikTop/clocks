<script setup>
defineProps({
  status: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <div class="inline-flex items-center space-x-2">
    <span
      class="badge px-3 py-1 text-sm text-white font-medium"
      :class="status ? 'badge-success' : 'badge-error'"
    >
      <span class="mr-1">
        {{ status ? '✓' : '✗' }}
      </span>
      {{ status ? 'Online' : 'Offline' }}
    </span>
  </div>
</template>
