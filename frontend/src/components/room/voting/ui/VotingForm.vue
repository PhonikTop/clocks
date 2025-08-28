<script setup>
import { ref, computed } from "vue";

const emit = defineEmits(["vote"]);

const guessValue = ref("");

const isValid = computed(() => {
  return /^\d+$/.test(guessValue.value) && Number(guessValue.value) > 0 && Number(guessValue.value) < 1000 && Number.isInteger(guessValue.value);
});

const handleSubmit = () => {
  if (!isValid.value) return;

  emit("vote", Number(guessValue.value));
  guessValue.value = "";
};
</script>

<template>
  <div class="card bg-base-100 p-4 shadow space-y-3 w-full max-w-sm">
    <label for="guess" class="font-semibold text-base">Ваша оценка:</label>
    <div class="flex items-center gap-2">
      <input
        v-model="guessValue"
        id="guess"
        type="number"
        min="0"
        step="1"
        placeholder="Введите часы"
        class="input input-bordered w-full"
      />
      <span class="text-sm text-gray-500">ч.</span>
    </div>

    <button
      class="btn btn-primary w-full"
      :disabled="!isValid"
      @click="handleSubmit"
    >
      OK
    </button>
  </div>
</template>
