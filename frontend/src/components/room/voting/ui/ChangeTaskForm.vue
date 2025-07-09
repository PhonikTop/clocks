<script setup>
import { ref } from "vue";

const emit = defineEmits(["submitted"]);

const localTaskName = ref("");

const handleSubmit = () => {
  if (!localTaskName.value.trim()) return;
  emit("submitted", localTaskName.value.trim());
  localTaskName.value = "";
};
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <input v-model="localTaskName" type="text" placeholder="Название комнаты" />
    <button type="submit">Сохранить</button>
  </form>
</template>
