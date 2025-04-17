<script setup>
defineEmits(["restartMeeting", "nextMeeting", "endMeeting"]);
</script>

<template>
  <div>
    <label>Общая оценка:</label>
    <div><span></span> ч.</div>
    <div>
      <button @click="$emit('restartMeeting')">Перезапустить</button>
      <button @click="$emit('nextMeeting')">Далее</button>
      <button @click="$emit('endMeeting')">Завершить</button>
    </div>
  </div>
</template>
