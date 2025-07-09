<script setup>
import ConnectionStatus from "@/components/room/ui/ConnectionStatus.vue";
import { ROOM_STATES } from "@/composables/room/useRoomState";

defineProps({
  roomId: String,
  taskName: String,
  isConnected: Boolean,
  roomState: String,
});

defineEmits(["leave-room"]);
</script>

<template>
  <header class="room-header">
    <ConnectionStatus :status="isConnected" />
    <h1>Комната {{ roomId }}</h1>
    <h1 v-if="roomState !== ROOM_STATES.WAITING">{{ taskName }}</h1>
    <button @click="$emit('leave-room')">Выйти из комнаты</button>
  </header>
</template>
