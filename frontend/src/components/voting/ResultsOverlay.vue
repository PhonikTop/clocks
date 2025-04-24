<script setup>
defineEmits(["restartMeeting", "nextMeeting", "endMeeting"]);
defineProps({
  resultsVotes: {
    type: Object,
    required: true,
  },
  averageScore: {
    type: Number,
    required: true,
    validator: (value) => Number.isInteger(value),
  },
});
</script>

<template>
  <div>
    <div>
      <div v-for="(user, id) in resultsVotes" :key="id">
        <div>{{ user.nickname }}</div>
        <div>{{ user.vote }}</div>
      </div>
    </div>
    <label>Общая оценка:</label>
    <div>
      <span>{{ averageScore }}</span> ч.
    </div>
    <div>
      <button @click="$emit('restartMeeting')">Перезапустить</button>
      <button @click="$emit('nextMeeting')">Далее</button>
      <button @click="$emit('endMeeting')">Завершить</button>
    </div>
  </div>
</template>
