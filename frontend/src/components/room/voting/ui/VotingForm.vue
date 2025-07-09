<script setup>
import { ref, computed } from "vue";

const emit = defineEmits(["vote"]);

const guessValue = ref("");

const isValid = computed(() => {
  return Number(guessValue.value) > 0;
});

const handleSubmit = () => {
  if (!isValid.value) return;

  emit("vote", Number(guessValue.value));
  guessValue.value = "";
};
</script>

<template>
  <div>
    <label for="guess">Ваша оценка:</label>
    <div>
      <input
        v-model="guessValue"
        id="guess"
        type="number"
        min="0"
        step="1"
        placeholder="Введите часы"
      />
      ч.
    </div>
    <button @click="handleSubmit" :disabled="!isValid">OK</button>
  </div>
</template>
