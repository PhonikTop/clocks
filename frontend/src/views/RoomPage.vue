<script setup>
import { computed, ref, onBeforeMount, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import VotersList from "@/components/voting/VotersList.vue";
import ObserversList from "@/components/voting/ObserversList.vue";
import VotingForm from "@/components/voting/VotingForm.vue";
import ResultsOverlay from "@/components/voting/ResultsOverlay.vue";
import ConnectionStatus from "@/components/ui/ConnectionStatus.vue";
import ChangeTaskForm from "@/components/voting/ChangeTaskForm.vue";

import useRoom from "@/composables/useRoom";
import useUser from "@/composables/useUser";
import useMeeting from "@/composables/useMeeting";

import { useRoomWebSocket } from "@/composables/useWebSocket";

const route = useRoute();
const router = useRouter();
const roomId = computed(() => route.params.room_id);

const roomState = ref("waiting"); // ['waiting', 'voting', 'waiting_players', 'results']

const currentMeeting = ref();
const taskName = ref("");

const { participants, fetchParticipants, currentRoom, fetchRoomDetails } =
  useRoom();
const { currentUser, error: userError, getCurrentUser } = useUser();
const {
  meetingRoom,
  getMeeting,
  createMeeting,
  endMeeting,
  restartMeeting,
  setMeetingTask,
} = useMeeting();

const token = ref(localStorage.getItem("token"));
const currentUserId = ref("");

const { isConnected, connect, sendMessage, addMessageHandler } =
  useRoomWebSocket(
    `${process.env.VUE_APP_WS_BASE_URL}room/${roomId.value}/?token=${token.value}`
  );

const votes = ref([]);
const allVoted = computed(() => {
  const voters = Object.values(participants.value).filter(
    (p) => p.role === "voter"
  );
  return voters.length > 0 && votes.value.length === voters.length;
});

const resultsVotes = ref({});
const averageScore = ref();

const userRole = ref();
const userNickname = ref();

const redirectToLogin = () => router.push({ name: "Login" });

const updateMeetingTaskName = async (newName) => {
  taskName.value = newName;
  await setMeetingTask(currentMeeting.value, taskName.value);
};

const startVoting = async () => {
  roomState.value = "voting";
  await createMeeting(roomId.value, taskName.value);
};

const handleVote = (hours) => {
  if (!currentUserId.value) return;

  sumbitVote(hours);

  if (!votes.value.includes(currentUserId.value)) {
    votes.value.push(currentUserId.value);
  }

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
    if (!votes.value.includes(msg.user)) {
      votes.value.push(msg.user);
    }
  });

  addMessageHandler("results", (msg) => {
    roomState.value = "results";
    resultsVotes.value = msg.votes;
    averageScore.value = msg.average_score;
    console.log(resultsVotes.value);
  });

  addMessageHandler("task_name_changed", (msg) => {
    taskName.value = msg.new_task_name;
  });

  addMessageHandler("meeting_started", async (msg) => {
    await getMeeting(msg.id);
    currentMeeting.value = msg.id;
    localStorage.setItem("active_meeting_id", msg.id);
    taskName.value = meetingRoom.value.task_name;
    roomState.value = "voting";
  });

  addMessageHandler("voted_users_update", (msg) => {
    votes.value = msg.voted_users;
  });

  addMessageHandler("meeting_change_status", async (msg) => {
    if (msg.status == "restart") {
      roomState.value = "voting";
      votes.value = [];
    } else if (msg.status == "next") {
      roomState.value = "waiting";
      currentMeeting.value = null;
      votes.value = [];
    } else if (msg.status == "ended") {
      redirectToLogin();
    }
  });
};

const sumbitVote = async (vote) => {
  await sendMessage({
    action: "submit_vote",
    vote: `${vote}`,
    token: token.value,
  });
};

const changeMeetingStatus = async (new_status) => {
  await sendMessage({
    action: "change_meeting_status",
    status: `${new_status}`,
  });
};

const handleRestartMeeting = () => {
  restartMeeting(currentMeeting.value);
  changeMeetingStatus("restart");
};

const handleNextMeeting = async () => {
  changeMeetingStatus("next");
};

const handleEndMeeting = () => {
  endMeeting(currentMeeting.value);
  changeMeetingStatus("ended");
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
    userRole.value = currentUser.value.role;
    userNickname.value = currentUser.value.nickname;
    localStorage.setItem("user_uuid", currentUserId.value);

    await fetchRoomDetails(roomId.value);
    if (currentRoom.value.active_meeting_id != null) {
      currentMeeting.value = currentRoom.value.active_meeting_id;
      localStorage.setItem(
        "active_meeting_id",
        currentRoom.value.active_meeting_id
      );
      roomState.value = "voting";
    }

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
      <ConnectionStatus :status="isConnected" />
      <h1>Комната {{ roomId }}</h1>
      <h1 v-if="roomState !== 'waiting'">{{ taskName }}</h1>
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
      <ChangeTaskForm @roomNameUpdated="updateMeetingTaskName" />
      <VotingForm @vote="handleVote" />
    </div>

    <!-- Состояние: Ожидание игроков -->
    <div v-if="roomState === 'waiting_players'">
      <p>Ожидаем остальных участников...</p>
      <VotingForm v-if="!votes[currentUserId]" @vote="handleVote" />
    </div>

    <!-- Общая секция участников -->
    <div>
      <VotersList
        :participants="participants"
        :votes="votes"
        v-if="roomState !== 'results'"
      />
      <ObserversList
        :participants="participants"
        v-if="roomState !== 'results'"
      />
    </div>

    <!-- Результаты -->
    <ResultsOverlay
      :resultsVotes="resultsVotes"
      :averageScore="averageScore"
      @restartMeeting="handleRestartMeeting"
      @nextMeeting="handleNextMeeting"
      @endMeeting="handleEndMeeting"
      v-if="roomState === 'results'"
    />
  </div>
</template>
