<script setup lang="ts">
import ConnectionStatus from "@/components/room/ui/ConnectionStatus.vue";
import { ROOM_STATES } from "@/composables/room/useRoomState";
import { ref } from "vue";

defineProps({
  roomName: String,
  taskName: String,
  isConnected: Boolean,
  roomState: String,
});

const cooldown = ref(0)
const isCooldown = ref(false)

function startCooldown(seconds: number) {
  cooldown.value = seconds
  isCooldown.value = true

  const interval = setInterval(() => {
    cooldown.value--
    if (cooldown.value <= 0) {
      clearInterval(interval)
      isCooldown.value = false
    }
  }, 1000)
}

function handleRestartButton() {
  startCooldown(10);
  emit('restart-meeting');
}

const emit = defineEmits(["leave-room", "restart-meeting"]);
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
    <div class="flex"> 
      <button v-if="roomState != ROOM_STATES.WAITING" class="btn btn-sm btn-dash" :disabled="isCooldown" @click="handleRestartButton">
        Перезагрузить голосование
      </button>
      <button class="btn btn-sm text-white btn-error ml-3" @click="$emit('leave-room')">
        Выйти из комнаты
      </button>
    </div>
  </header>
</template>
