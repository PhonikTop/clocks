<script setup lang="ts">
import { Participant, ParticipantInfo } from "@/composables/api/useRoomAPI";
import { computed, Ref, ref } from "vue";

const props = defineProps<{
  participants: Participant;
  votes: string[];
}>();

const emit = defineEmits<{
  (e: 'kick-user', id: string): void;
}>();

// Получаем только участников с ролью "voter" и сортируем по имени
const voters = computed(() =>
  Object.entries(props.participants)
    .filter(([, info]) => info.role === "voter")
    .sort(([, aInfo], [, bInfo]) => aInfo.nickname.localeCompare(bInfo.nickname))
);

// Выбранный голосующий
const selectedVoter: Ref<null | { id: string; info: ParticipantInfo }> = ref(null);

// Обработчик клика по участнику
function onVoterClick([id, info]: [string, ParticipantInfo]) {
  if (selectedVoter.value?.id === id) {
    selectedVoter.value = null;
  } else {
    selectedVoter.value = { id, info };
  }
}
</script>

<template>
  <div class="card bg-base-100 shadow p-4 h-auto">
    <h2 class="text-lg font-semibold mb-3">
      Голосующие
    </h2>

    <div
      v-if="voters.length"
      class="space-y-2 overflow-y-auto"
    >
      <div
        v-for="[id, participant] in voters"
        :key="id"
        class="space-y-1"
      >
        <div
          class="flex items-center justify-between p-2 rounded-lg hover:bg-base-200 transition cursor-pointer"
          @click="onVoterClick([id, participant])"
        >
          <div class="flex items-center gap-3">
            <div class="avatar placeholder w-8 h-8 rounded-full flex justify-center items-center bg-neutral text-neutral-content">
              <span class="text-black text-sm leading-none">
                {{ participant.nickname.charAt(0).toUpperCase() }}
              </span>
            </div>
            <span class="text-base">{{ participant.nickname }}</span>
          </div>

          <Transition
            mode="out-in"
            enter-active-class="transition transform duration-500"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition transform duration-300"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-90"
          >
            <div
              :key="props.votes.includes(id) ? 'voted' : 'waiting'"
              :class="[
                'badge text-sm text-white',
                props.votes.includes(id) ? 'badge-success' : 'badge-warning'
              ]"
              aria-label="Статус голосования"
            >
              {{ props.votes.includes(id) ? '✓' : '⌛' }}
            </div>
          </Transition>
        </div>

        <Transition
          enter-active-class="transition transform duration-300"
          enter-from-class="max-h-0 opacity-0 scale-y-90"
          enter-to-class="max-h-40 opacity-100 scale-y-100"
          leave-active-class="transition transform duration-200"
          leave-from-class="max-h-40 opacity-100 scale-y-100"
          leave-to-class="max-h-0 opacity-0 scale-y-90"
        >
          <div
            v-if="selectedVoter?.id === id"
            class="flex justify-center"
          >
            <button
              class="btn btn-primary w-full mt-1"
              @click="emit('kick-user', selectedVoter.id)"
            >
              Кикнуть {{ selectedVoter.info.nickname }}
            </button>
          </div>
        </Transition>
      </div>
    </div>

    <div
      v-else
      class="text-sm text-gray-400 italic"
    >
      Нет голосующих участников.
    </div>
  </div>
</template>