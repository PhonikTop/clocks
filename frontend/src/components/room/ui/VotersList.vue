<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  participants: {
    type: Object,
    required: true,
    validator: (value) =>
      Object.values(value).every((p) => "nickname" in p && "role" in p),
  },
  votes: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['kick-user']);

const voters = computed(() =>
  Object.entries(props.participants)
    .filter(([, participant]) => participant.role === "voter")
    .sort((a, b) => a[1].nickname.localeCompare(b[1].nickname))
);

const selectedVoter = ref(null);

function onVoterClick(participant) {
  if (selectedVoter.value?.id === participant[0]) {
    selectedVoter.value = null;
  } else {
    selectedVoter.value = { id: participant[0], ...participant[1] };
  }
}
</script>

<template>
  <div class="card bg-base-100 shadow p-4 h-auto">
    <h2 class="text-lg font-semibold mb-3">Голосующие</h2>

    <div v-if="voters.length" class="space-y-2 overflow-y-auto">
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
              :key="votes.includes(id) ? 'voted' : 'waiting'"
              :class="[
                'badge text-sm text-white',
                votes.includes(id) ? 'badge-success' : 'badge-warning'
              ]"
              aria-label="Статус голосования"
            >
              {{ votes.includes(id) ? '✓' : '⌛' }}
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
          <div v-if="selectedVoter?.id === id" class="flex justify-center">
            <button
              @click="emit('kick-user', selectedVoter.id)"
              class="btn btn-primary w-full mt-1"
            >
              Кикнуть {{ selectedVoter.nickname }}
            </button>
          </div>
        </Transition>
      </div>
    </div>

    <div v-else class="text-sm text-gray-400 italic">
      Нет голосующих участников.
    </div>
  </div>
</template>