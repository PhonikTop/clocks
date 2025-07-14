<script setup>
import ConnectionStatus from "@/components/room/ui/ConnectionStatus.vue";
import { ROOM_STATES } from "@/composables/room/useRoomState";

defineProps({
  roomName: String,
  taskName: String,
  isConnected: Boolean,
  roomState: String,
});

defineEmits(["leave-room"]);
</script>

<template>
  <header
    class="w-full bg-base-200 shadow-md p-4 rounded-box flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
  >
    <div class="flex items-center gap-4">
      <ConnectionStatus :status="isConnected" />
      <div>
        <h1 class="text-lg font-semibold">Комната "{{ roomName }}"</h1>
        <Transition
          enter-active-class="transition-opacity duration-700"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
          leave-active-class="transition-opacity duration-500"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
          mode="out-in"
        >
          <h2
            v-if="roomState !== ROOM_STATES.WAITING"
            :key="taskName"
            class="text-sm text-gray-500"
          >
            {{ taskName }}
          </h2>
        </Transition>
      </div>
    </div>

    <button class="btn btn-sm text-white btn-error" @click="$emit('leave-room')">
      Выйти из комнаты
    </button>
  </header>
</template>
