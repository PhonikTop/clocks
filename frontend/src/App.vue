<script setup>
import { provide } from 'vue';
import { useToasts } from '@/composables/useToasts.ts';
import ToastManager from "@/components/ToastManager.vue";

const toast = useToasts()

provide('toast', toast)
</script>

<template>
  <RouterView />
  <ToastManager/>
</template>
