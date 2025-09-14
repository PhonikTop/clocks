<script setup lang="ts">
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
  <form
    class="flex flex-col sm:flex-row items-stretch gap-3"
    @submit.prevent="handleSubmit"
  >
    <input
      v-model="localTaskName"
      type="text"
      placeholder="Название задачи"
      maxlength="35"
      class="input input-bordered w-full"
    >
    <button
      type="submit"
      class="btn btn-primary"
    >
      Сохранить
    </button>
  </form>
</template>
