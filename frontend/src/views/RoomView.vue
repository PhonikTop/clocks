<template>
  <div class="content">
    <div class="wrapper">
      <component :is="activeComponent" v-if="activeComponent" />
      <ObserversWrapper
        v-show="showObserversWrapper"
        :participants="participants"
      />
      <UserWrapper
        v-show="showUserWrapper"
        :participants="participants"
        :votes="votes"
      />
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
  },
  data () {
    return {
      currentBlock: 'StartBlock',
      showObserversWrapper: true,
      showUserWrapper: true,
      participants: {},
      votes: {}
    }
  },
  computed: {
    activeComponent () {
      switch (this.currentBlock) {
        case 'StartBlock':
          return StartBlock
        case 'GuessBlock':
          return GuessBlock
        case 'TotalBlock':
          return TotalBlock
        case 'WaitBlock':
          return WaitBlock
        default:
          return null
      }
    }
  }
  }
}
</script>
<style scoped>
@import '@/assets/styles/app.css';

.wrapper {
  max-width: 580px;
  height: 300px;
  margin: 0 auto;
  background: #F5F5F5;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}
</style>
