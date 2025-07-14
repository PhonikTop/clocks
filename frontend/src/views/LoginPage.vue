<script setup>
import { onMounted } from "vue";
import { ref } from "vue";
import { useRouter } from "vue-router";
import useRoom from "@/composables/api/useRoomAPI";
import useUser from "@/composables/api/useUserAPI";

const router = useRouter();
const username = ref("");
const isObserver = ref(false);
const selectRoomId = ref("");

const { roomList, fetchRoomList } = useRoom();
const { joinRoom } = useUser();

const enterRoom = async () => {
  const role = isObserver.value ? "observer" : "voter";
  await joinRoom(selectRoomId.value, username.value, role);
  router.push({
    name: "Room",
    params: { room_id: selectRoomId.value },
  });
};

onMounted(async () => {
  await fetchRoomList();
});
</script>

<template>
  <div
    class="min-h-screen bg-gray-100 flex items-center justify-center p-4"
  >
    <div class="bg-white shadow-lg rounded-xl max-w-md w-full p-8">
      <h1 class="text-3xl font-semibold text-center text-gray-700 mb-8">
        Вход в комнату
      </h1>

      <form @submit.prevent="enterRoom" class="space-y-6">
        <div>
          <label
            for="username"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            Имя пользователя
          </label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            placeholder="Введите имя"
            class="input"
          />
        </div>

        <div>
          <label
            for="room"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            ID комнаты
          </label>
          <select id="room" v-model="selectRoomId" required class="select">
            <option disabled value="">Выберите комнату</option>
            <option v-for="room in roomList" :key="room.id" :value="room.id">
              {{ room.name }}
            </option>
          </select>
        </div>

        <div class="flex items-center space-x-2">
          <input
            id="observer"
            type="checkbox"
            v-model="isObserver"
            class="checkbox"
          />
          <label for="observer" class="select-none">
            Войти как наблюдатель
          </label>
        </div>

        <button
          type="submit"
          class="btn btn-primary"
          :disabled="!username || !selectRoomId"
        >
          Войти
        </button>
      </form>
    </div>
  </div>
</template>
