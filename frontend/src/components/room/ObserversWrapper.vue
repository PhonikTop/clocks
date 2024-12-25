<template>
  <div class="observers__wrapper">
      <h3>Наблюдатели</h3>
      <div class="observers">
        <div v-for="observer in observers" :key="observer.nickname">{{ observer.nickname }}</div>
      </div>
  </div>
</template>
<script>
export default {
  props: {
    participants: {
      type: Object,
      required: true
    }
  },
  computed: {
    observers () {
      return Object.values(this.participants).filter(participant => participant.role === 'observer')
    }
  }
}
</script>
<style>
.observers__wrapper {
  position: fixed;
  top: 0;
  right: 20px;
  text-align: right;
}

.observers h3 {
  font-size: 1.2rem;
  color: #6B6B6B;
}

.observers div{
  margin-top: 10px;
  display: flex;
  justify-content: right;
  gap: 10px;
}
</style>
