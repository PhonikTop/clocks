<script setup>
import { useRoute, useRouter } from "vue-router";
import { computed } from "vue";

const route = useRoute();
const router = useRouter();

const roomId = computed(() => route.params.room_id);

const leaveRoom = () => {
  router.push({ name: "Login" });
};
</script>

<template>
  <h1>Комната {{ roomId }}</h1>
  <div class="room">
    <button @click="leaveRoom">Выйти из комнаты</button>
  </div>
</template>
