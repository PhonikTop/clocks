<script setup lang="ts">
import ChangeTaskForm from "@/components/room/voting/ui/ChangeTaskForm.vue";

defineEmits(["start-voting"]);
</script>

<template>
  <ChangeTaskForm @submitted="$emit('start-voting', $event)" />
</template>
