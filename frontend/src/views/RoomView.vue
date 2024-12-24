<template>
  <div class="content">
    <div class="wrapper">
      <StartBlock/>
      <GuessBlock/>
      <TotalBlock/>
      <WaitBlock/>
      <ObserversWrapper/>
      <UserWrapper/>
    </div>
  </div>
</template>
<script>
import StartBlock from '@/components/room/StartBlock.vue'
import GuessBlock from '@/components/room/GuessBlock.vue'
import TotalBlock from '@/components/room/TotalBlock.vue'
import WaitBlock from '@/components/room/WaitBlock.vue'
import ObserversWrapper from '@/components/room/ObserversWrapper.vue'
import UserWrapper from '@/components/room/UserWrapper.vue'

export default {
  name: 'RoomView',
  components: {
    StartBlock,
    GuessBlock,
    TotalBlock,
    WaitBlock,
    ObserversWrapper,
    UserWrapper
  }
}
</script>
<style scoped>
@import '@/assets/styles/app.css';

.wrapper {
  max-width: 580px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
</style>
