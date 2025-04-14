<script setup>
import { onMounted } from "vue";
import { ref } from "vue";
import { useRouter } from "vue-router";
import useRoom from "@/composables/useRoom";

const router = useRouter();
const username = ref("");
const roomId = ref("");

const { roomList, fetchRoomList } = useRoom();

const enterRoom = () => {
  router.push({
    name: "Room",
    params: { room_id: roomId.value },
  });
};

onMounted(async () => {
  await fetchRoomList();
});
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
          <option v-for="room in roomList" :key="room.id" :value="room.id">
            {{ room.name }}
          </option>
        </select>
      </div>
      <button type="submit">Войти</button>
    </form>
  </div>
</template>
