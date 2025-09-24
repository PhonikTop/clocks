<script setup lang="ts">
import ConnectionStatus from "@/components/room/ui/ConnectionStatus.vue";
import { ROOM_STATES } from "@/composables/room/useRoomState";
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { useTimerStore } from "@/stores/roomTimer";

const props = defineProps<{
  endTimestamp: number | null,
  roomName: string,
  taskName: string,
  isConnected: boolean,
  roomState: string,
}>();

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

const emit = defineEmits(["leave-room", "restart-meeting", "start-timer", "reset-timer"]);

const timerStore = useTimerStore()

let intervalId: number | undefined;

function updateTime() {
  if (props.endTimestamp) {
    timerStore.updateTime(props.endTimestamp)
  }
}

const resetTimerConfirm = ref<boolean>(false)
const hoverTimerButtonHover = ref<boolean>()

const displayText = computed(() => 
  resetTimerConfirm.value
    ? 'Вы точно хотите сбросить таймер?'
    : hoverTimerButtonHover.value
      ? 'Сбросить таймер'
      : timerStore.formattedTime
)

watch(
  () => resetTimerConfirm.value,
  (newVal) => {
    if (newVal) {
      setTimeout(() => {
        resetTimerConfirm.value = false
      }, 5000)
    }
  }
)

const handleRoomTimerReset = async () => {
  if (resetTimerConfirm.value === false) {
    resetTimerConfirm.value = true
  } else {
    emit('reset-timer')
    resetTimerConfirm.value = false
  }
}

onMounted(() => {
  updateTime();
  intervalId = window.setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
});

watch(() => props.endTimestamp, () => {
  updateTime();
});
</script>

<template>
  <header
    class="w-full bg-base-200 shadow-md p-4 rounded-box flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
  >
    <div class="flex items-center gap-4">
      <ConnectionStatus :status="isConnected" />
      <div>
        <h1 class="text-lg font-semibold">
          Комната "<span class="whitespace-nowrap">{{ props.roomName }}</span>"
        </h1>
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
            v-if="props.roomState !== ROOM_STATES.WAITING"
            :key="taskName"
            class="text-sm text-gray-500"
          >
            {{ props.taskName }}
          </h2>
        </Transition>
      </div>
    </div>
    <div class="flex flex-wrap gap-2 sm:gap-3">
      <button
        v-if="props.endTimestamp"
        class="btn btn-sm text-white btn-warning ml-3 text-lg font-semibold"
        @mouseenter="hoverTimerButtonHover = true"
        @mouseleave="hoverTimerButtonHover = false"
        @click.prevent="handleRoomTimerReset"
      >
        {{ displayText }}
      </button>
      <div class="flex flex-wrap gap-2 sm:gap-3" v-else>
        <button 
          class="btn btn-sm text-white btn-warning"
          @click.prevent="emit('start-timer', 5)"
        >
          5 Минут
        </button>
        <button
          class="btn btn-sm text-white btn-warning"
          @click.prevent="emit('start-timer', 10)"
        >
          10 Минут
        </button>
        <button
          class="btn btn-sm text-white btn-warning"
          @click.prevent="emit('start-timer', 15)"
        >
          15 Минут
        </button>
      </div>
    </div>
    <div class="flex">
      <button
        v-if="props.roomState != ROOM_STATES.WAITING"
        class="btn btn-sm btn-dash"
        :disabled="isCooldown"
        @click="handleRestartButton"
      >
        Перезагрузить голосование
      </button>
      <button
        class="btn btn-sm text-white btn-error ml-3"
        @click="$emit('leave-room')"
      >
        Выйти из комнаты
      </button>
    </div>
  </header>
</template>
