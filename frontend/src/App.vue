<script setup>
import { provide } from 'vue';
import { useToasts } from '@/composables/useToasts.js';
import ToastManager from "@/components/ToastManager.vue";

const toast = useToasts()

provide('toast', toast)
</script>

<template>
  <RouterView />
  <ToastManager/>
</template>
