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
  <form @submit.prevent="handleSubmit" class="flex flex-col sm:flex-row items-stretch gap-3">
    <input
      v-model="localTaskName"
      type="text"
      placeholder="Название комнаты"
      class="input input-bordered w-full"
    />
    <button type="submit" class="btn btn-primary">
      Сохранить
    </button>
  </form>
</template>
