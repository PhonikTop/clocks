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
  <div class="voter-list">
    <div v-for="[id, participant] in observers" :key="id" class="voter-item">
      <span class="nickname">{{ participant.nickname }}</span>
    </div>
  </div>
</template>
