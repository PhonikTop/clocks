<script setup>
import { computed, ref, onBeforeMount, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import VotersList from "@/components/voting/VotersList.vue";
import ObserversList from "@/components/voting/ObserversList.vue";
import VotingForm from "@/components/voting/VotingForm.vue";
import ResultsOverlay from "@/components/voting/ResultsOverlay.vue";

import useRoom from "@/composables/useRoom";
import useUser from "@/composables/useUser";
import useMeeting from "@/composables/useMeeting";

import { useRoomWebSocket } from "@/composables/useWebSocket";

const route = useRoute();
const router = useRouter();
const roomId = computed(() => route.params.room_id);

const roomState = ref("waiting"); // ['waiting', 'voting', 'waiting_players', 'results']

const taskName = ref("");

const { participants, fetchParticipants } = useRoom();
const { currentUser, error: userError, getCurrentUser } = useUser();
const { createMeeting } = useMeeting();

const { isConnected, connect, sendMessage, addMessageHandler } =
  useRoomWebSocket(`ws://localhost/ws/room/${roomId.value}/`);

const token = ref(localStorage.getItem("token"));
const currentUserId = ref("");

const votes = ref({});
const allVoted = computed(() => {
  const voters = Object.values(participants.value).filter(
    (p) => p.role === "voter"
  );
  return voters.length > 0 && Object.keys(votes.value).length === voters.length;
});

const resultsVotes = ref({});
const averageScore = ref();

const redirectToLogin = () => router.push({ name: "Login" });

const startVoting = async () => {
  roomState.value = "voting";
  await createMeeting(roomId.value, taskName.value);
};

const handleVote = (hours) => {
  if (!currentUserId.value) return;

  sumbitVote(hours);

  votes.value[currentUserId.value] = hours;

  roomState.value = allVoted.value ? "results" : "waiting_players";
};

const setupHandlers = () => {
  addMessageHandler("user_joined", (msg) => {
    if (msg?.user) {
      Object.assign(participants.value, msg.user);
    } else {
      console.error("Invalid user_joined message:", msg);
    }
  });

  addMessageHandler("user_voted", (msg) => {
    votes.value[msg.user] = 1;
  });

  addMessageHandler("results", (msg) => {
    roomState.value = "results";
    resultsVotes.value = msg.votes;
    averageScore.value = msg.average_score;
    console.log(resultsVotes.value);
  });
};

const sumbitVote = async (vote) => {
  await sendMessage({
    action: "submit_vote",
    vote: `${vote}`,
    user_id: currentUserId.value,
  });
};

const handleRestartMeeting = () => {
  roomState.value = "voting";
};

const handleNextMeeting = () => {
  roomState.value = "waiting";
};

const handleEndMeeting = () => {
  redirectToLogin();
};

const leaveRoom = () => router.push({ name: "Login" });

onBeforeMount(async () => {
  if (!token.value) {
    redirectToLogin();
    return;
  }

  await getCurrentUser(roomId.value, token.value);
  if (userError.value?.status === 403) {
    redirectToLogin();
    return;
  }

  if (currentUser.value) {
    currentUserId.value = currentUser.value.user_uuid;
    localStorage.setItem("user_uuid", currentUserId.value);

    await fetchParticipants(roomId.value);
  }
});

onMounted(async () => {
  try {
    await connect();
    setupHandlers();
  } catch (err) {
    console.error("Connection failed:", err);
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
    <ResultsOverlay
      @restartMeeting="handleRestartMeeting"
      @nextMeeting="handleNextMeeting"
      @endMeeting="handleEndMeeting"
      v-if="roomState === 'results'"
    />
  </div>
</template>
