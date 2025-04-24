<template>
  <form @submit.prevent="handleSubmit">
    <input v-model="localRoomName" type="text" placeholder="Название комнаты" />
    <button type="submit">Сохранить</button>
  </form>
</template>

<script setup>
import { ref } from "vue";

const emit = defineEmits(["roomNameUpdated"]);
1;
const localRoomName = ref("");

const handleSubmit = () => {
  if (!localRoomName.value.trim()) return;
  emit("roomNameUpdated", localRoomName.value.trim());
  localRoomName.value = "";
};
</script>
