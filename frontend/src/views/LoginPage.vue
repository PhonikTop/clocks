<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const roomId = ref("");

const rooms = ref([
  { id: "1", name: "Room 1" },
  { id: "2", name: "Room 2" },
  { id: "3", name: "Room 3" },
  { id: "4", name: "Room 4" },
  { id: "5", name: "Room 5" },
]);

const enterRoom = () => {
  router.push({
    name: "Room",
    params: { room_id: roomId.value },
  });
};
</script>

<template>
  <div class="home">
    <h1>Вход в комнату</h1>
    <form @submit.prevent="enterRoom">
      <div>
        <label>Имя пользователя:</label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>ID комнаты:</label>
        <select v-model="roomId" required>
          <option disabled value="">Выберите комнату</option>
          <option v-for="room in rooms" :key="room.id" :value="room.id">
            {{ room.name }}
          </option>
        </select>
      </div>
      <button type="submit">Войти</button>
    </form>
  </div>
</template>
