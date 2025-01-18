<template>
  <div class="content">
    <div class="wrapper">
      <component :is="activeComponent" v-if="activeComponent"
        :room="room"
      />
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
import api from '@/services/api'
import WebSocketClient from '@/services/WebSocketClient'
import Room from '@/services/RoomHandler'

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
      votes: [],
      wsClient: null,
      room: null
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
  },
  methods: {
    async checkAuthorization (roomId) {
      try {
        const token = localStorage.getItem('authToken')
        if (!token) {
          throw new Error('Token not found')
        }

        await api.get(`user/${roomId}/`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      } catch (error) {
        if (error.response?.status === 403) {
          console.error('Authorization failed:', error)
          localStorage.clear()
          this.$router.push('/')
        } else {
          console.error('Error during authorization check:', error)
        }
      }
    },
    async fetchParticipants (roomId) {
      try {
        const response = await api.get(`room/${roomId}/participants/`)
        this.participants = response.data.participants
      } catch (error) {
        console.error('Error fetching participants:', error)
      }
    },

    async connectWebSocket () {
      const roomId = this.$route.params.id
      this.wsClient = new WebSocketClient(`ws://localhost/ws/room/${roomId}/`) // Замените localhost на ваш реальный адрес
      this.room = new Room(this.wsClient, this.participants, this.votes)

      try {
        await this.wsClient.connect()
      } catch (error) {
        console.error('Ошибка при подключении к WebSocket:', error)
      }
    }
  },
  async mounted () {
    const roomId = this.$route.params.id
    await this.checkAuthorization(roomId)
    await this.fetchParticipants(roomId)

    await this.connectWebSocket()
  },
  beforeUnmount () {
    if (this.wsClient) {
      this.wsClient.disconnect()
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
