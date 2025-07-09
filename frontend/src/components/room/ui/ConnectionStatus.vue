<script setup>
defineProps({
  status: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <div>
    <span v-if="status === true">✓ Online</span>
    <span v-else>✗ Offline</span>
  </div>
</template>
