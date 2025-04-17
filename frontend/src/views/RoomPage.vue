<script setup>
import { onMounted, onBeforeMount } from "vue";
import { useRoute, useRouter } from "vue-router";
import { computed, ref } from "vue";
import VotersList from "@/components/voting/VotersList.vue";
import ObserversList from "@/components/voting/ObserversList.vue";
import VotingForm from "@/components/voting/VotingForm.vue";
import ResultsOverlay from "@/components/voting/ResultsOverlay.vue";
import useRoom from "@/composables/useRoom";
import useUser from "@/composables/useUser";
import useMeeting from "@/composables/useMeeting";

const route = useRoute();
const router = useRouter();
const roomId = computed(() => route.params.room_id);

const roomState = ref("waiting"); // ['waiting', 'voting', 'waiting_players', 'results']

const taskName = ref("");

const { participants, fetchParticipants } = useRoom();
const { error, getCurrentUser } = useUser();
const { createMeeting } = useMeeting();

const token = ref(localStorage.getItem("token"));
const currentUserId = ref("1");

const votes = ref({});

const allVoted = computed(() => {
  const voters = Object.values(participants).filter((p) => p.role === "voter");
  return Object.keys(votes.value).length === voters.length;
});

const startVoting = async () => {
  roomState.value = "voting";
  await createMeeting(roomId.value, taskName.value);
};

const handleVote = (hours) => {
  votes.value[currentUserId.value] = hours;

  if (allVoted.value) {
    roomState.value = "results";
  } else {
    roomState.value = "waiting_players";
  }
};

const leaveRoom = () => router.push({ name: "Login" });

onMounted(async () => {
  await fetchParticipants(roomId.value);
});

onBeforeMount(async () => {
  await getCurrentUser(roomId.value, token.value);
  if (error.value?.status === 403) {
    router.push({ name: "Login" });
  }
});
</script>

<template>
  <div>
    <header>
      <h1>Комната {{ roomId }}</h1>
      <button @click="leaveRoom">Выйти из комнаты</button>
    </header>

    <!-- Состояние: Ожидание начала -->
    <div v-if="roomState === 'waiting'">
      <div>
        <input
          v-model="taskName"
          placeholder="Введите название задачи"
          type="text"
        />
      </div>
      <button @click="startVoting">Начать голосование</button>
    </div>

    <!-- Состояние: Голосование -->
    <div v-if="roomState === 'voting'">
      <VotingForm @vote="handleVote" />
    </div>

    <!-- Состояние: Ожидание игроков -->
    <div v-if="roomState === 'waiting_players'">
      <p>Ожидаем остальных участников...</p>
      <VotingForm v-if="!votes[currentUserId]" @vote="handleVote" />
    </div>

    <!-- Общая секция участников -->
    <div>
      <VotersList :participants="participants" :votes="votes" />
      <ObserversList :participants="participants" />
    </div>

    <!-- Результаты -->
    <ResultsOverlay v-if="roomState === 'results'" />
  </div>
</template>
