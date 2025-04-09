<script setup>
import { computed } from "vue";

const props = defineProps({
  participants: {
    type: Object,
    required: true,
    validator: (value) =>
      Object.values(value).every((p) => "nickname" in p && "role" in p),
  },
  votes: {
    type: Object,
    required: true,
  },
});

const voters = computed(() =>
  Object.entries(props.participants)
    .filter(([, participant]) => participant.role === "voter")
    .sort((a, b) => a[1].nickname.localeCompare(b[1].nickname))
);
</script>

<template>
  <div class="voter-list">
    <div v-for="[id, participant] in voters" :key="id" class="voter-item">
      <span class="nickname">{{ participant.nickname }}</span>
      <span
        class="vote-indicator"
        :class="{ 'has-voted': votes[id] }"
        aria-label="Статус голосования"
      >
        {{ votes[id] ? "✓" : "⌛" }}
      </span>
    </div>
  </div>
</template>
