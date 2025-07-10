<script setup>
import { computed } from "vue";

const props = defineProps({
  participants: {
    type: Object,
    required: true,
    validator: (value) =>
      Object.values(value).every((p) => "nickname" in p && "role" in p),
  },
});

const observers = computed(() =>
  Object.entries(props.participants)
    .filter(([, participant]) => participant.role === "observer")
    .sort((a, b) => a[1].nickname.localeCompare(b[1].nickname))
);
</script>

<template>
  <div class="card bg-base-100 shadow-md p-4">
    <h2 class="text-lg font-semibold mb-3">Наблюдающие</h2>

    <div v-if="observers.length" class="space-y-2">
      <div
        v-for="[id, participant] in observers"
        :key="id"
        class="flex items-center gap-3 p-2 rounded-lg hover:bg-base-200 transition"
      >
        <div class="avatar placeholder w-8 h-8 rounded-full flex justify-center items-center bg-neutral text-neutral-content">
          <span class="text-black text-sm leading-none">
            {{ participant.nickname.charAt(0).toUpperCase() }}
          </span>
        </div>
        <span class="text-base">{{ participant.nickname }}</span>
      </div>
    </div>

    <div v-else class="text-sm text-gray-400 italic">
      Нет наблюдающих участников.
    </div>
  </div>
</template>
