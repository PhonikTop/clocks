<template>
  <div class="start-var">
      <form class="user-form" @submit.prevent="joinRoom">
          <select v-model="selectedRoom" name="room_select">
            <option v-for="room in rooms" :key="room.id" :value="room.id">
              {{ room.name }}
            </option>
          </select>
          <input id="name" name="nickname" placeholder="Введите имя" type="text" v-model="nickname" />
          <div class="observer">
            <input type="checkbox" name="is_observer" id="observer" v-model="isObserver" />
            <label for="observer"> Наблюдатель</label>
          </div>
          <button id="enter" type="submit">Далее</button>
      </form>
  </div>
</template>
<script>
import api from '@/services/api'

export default {
  data () {
    return {
      rooms: [],
      selectedRoom: null,
      nickname: '',
      isObserver: false
    }
  },
  methods: {
    async fetchRooms () {
      try {
        const response = await api.get('room/list/')
        this.rooms = response.data
      } catch (error) {
        console.error('Ошибка при загрузке комнат:', error)
      }
    },
    async joinRoom () {
      if (!this.selectedRoom || !this.nickname.trim()) {
        alert('Пожалуйста, заполните все поля.')
        return
      }
      const role = this.isObserver ? 'observer' : 'voter'
      const formData = new FormData()
      formData.append('nickname', this.nickname)
      formData.append('role', role)

      try {
        const response = await api.post(`user/join/${this.selectedRoom}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        const token = response.data.token
        const userUuid = response.data.user_uuid
        if (token) {
          localStorage.setItem('authToken', token)
        }
        if (userUuid) {
          localStorage.setItem('userUuid', userUuid)
        }
        this.$router.push(`/room/${this.selectedRoom}`)
      } catch (error) {
        console.error('Ошибка при присоединении к комнате:', error)
        alert('Произошла ошибка, попробуйте снова.')
      }
    }
  },
  mounted () {
    this.fetchRooms()
  }
}
</script>
<style>
.start-var {
  padding: 15px;
  border: 2.6px solid rgb(21,23,25);
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.5);
  width: 300px;
  height: auto;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 30px;
}
.user-form {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 15px;
  width: 100%;
  max-width: 300px;
  margin: 20px;
}

.user-form select,
.user-form input {
  padding: 8px;
  font-size: 16px;
  border: 2px solid var(--primary-color);
  border-radius: var(--border-radius);
}

.user-form button {
  padding: 10px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  font-size: 18px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: background-color 0.3s;
}

.user-form button:hover {
  background-color: #333;
  color: azure;
}

.observer {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
