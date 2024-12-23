<template>
  <div class="content">
    <div class="wrapper">
      <StartBlock/>
    </div>
  </div>
</template>
<script>
import StartBlock from '../components/room/StartBlock.vue'

export default {
  name: 'RoomView',
  components: {
    StartBlock
  }
}
</script>
<style scoped>
body {
  font-family:system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  margin: 0;
  padding: 0;
  color: #333;
}

.wrapper {
  max-width: 580px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.content {
  margin-top: 20px;
}

.start__block, .guess__block, .total__block, .wait__block {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.users__wrapper, .observers__wrapper {
  margin-top: 20px;
  text-align: center;
}

</style>
