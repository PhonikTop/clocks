<script setup>
import { ref, computed, onBeforeMount, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import RoomHeader from "@/components/room/ui/RoomHeader.vue";
import WaitingMeetingState from "@/components/room/voting/states/WaitingMeetingState.vue";
import VotingMeetingState from "@/components/room/voting/states/VotingMeetingState.vue";
import ResultsMeetingState from "@/components/room/voting/states/ResultsMeetingState.vue";
import ParticipantsSection from "@/components/room/ui/ParticipantsSection.vue";

import useRoomState from "@/composables/room/useRoomState";
import useMeetingManager from "@/composables/room/api/useMeetingManager";
import useRoomWebSocketHandler from "@/composables/room/useRoomWebSocketHandler";
import useRoomParticipants from "@/composables/room/useRoomParticipants";
import { useRoomWebSocket } from "@/composables/api/useWebSocket";

import useMeeting from "@/composables/api/useMeetingAPI";

const route = useRoute();
const router = useRouter();
const roomId = route.params.room_id 

const { roomState, ROOM_STATES, taskName, votes, resultsVotes, averageScore } =
  useRoomState();

const {
  participants,
  currentUser,
  currentUserId,
  fetchParticipants,
  getCurrentUser,
  userError,
} = useRoomParticipants(roomId);

const token = ref(localStorage.getItem("token"));

const userRole = ref("");

const redirectToLogin = () => router.push({ name: "Login" });

const { isConnected, connect, sendMessage, addMessageHandler } =
  useRoomWebSocket(
    `${process.env.VUE_APP_WS_BASE_URL}room/${roomId.value}/?token=${token.value}`
  );

const { currentMeeting } = useRoomWebSocketHandler(
  addMessageHandler,
  roomState,
  participants,
  votes,
  resultsVotes,
  averageScore,
  taskName,
  redirectToLogin
);

const { meetingRoom } = useMeeting();

const { getRoomMeeting, ...meetingActions } = useMeetingManager(
  roomState,
  sendMessage,
  currentMeeting
);

const handleVote = (voteValue) => {
  try {
    sendMessage({
      action: "submit_vote",
      vote: `${voteValue}`,
      token: token.value,
    });
  } catch (err) {
    console.error("Ошибка отправки голоса:", err);
  }
};

onBeforeMount(async () => {
  if (!token.value) redirectToLogin();

  try {
    await getCurrentUser();
    if (userError.value?.status === 403) {
      meetingRoom;
      redirectToLogin();
      return;
    }
    if (currentUser.value) {
      userRole.value = currentUser.value.role;
    }
  } catch (err) {
    redirectToLogin();
  }
  await fetchParticipants();
});

onMounted(async () => {
  try {
    await connect();
  } catch (err) {
    console.error("Ошибка подключения:", err);
  }
  if (currentMeeting.value == null) {
    const meeting = await getRoomMeeting(roomId);
    if (meeting?.id != null) {
      currentMeeting.value = meeting.id;
      localStorage.setItem("active_meeting_id", meeting.id);
      taskName.value = meeting.task_name;
      roomState.value = ROOM_STATES.VOTING;
    }
  }
});
</script>

<template>
  <div>
    <RoomHeader
      :room-id="roomId"
      :task-name="taskName"
      :is-connected="isConnected"
      :room-state="roomState"
      @leave-room="redirectToLogin"
    />

    <WaitingMeetingState
      v-if="roomState === ROOM_STATES.WAITING"
      v-model:task-name="taskName"
      @start-voting="(taskName) => meetingActions.startVoting(roomId, taskName)"
    />

    <VotingMeetingState
      v-else-if="roomState === ROOM_STATES.VOTING && userRole === 'voter'"
      @vote="handleVote"
      @update-task="meetingActions.updateMeetingTaskName"
    />

    <ParticipantsSection
      v-if="roomState !== ROOM_STATES.RESULTS"
      :participants="participants"
      :votes="votes"
    />

    <ResultsMeetingState
      v-if="roomState === ROOM_STATES.RESULTS"
      :results-votes="resultsVotes"
      :average-score="averageScore"
      @restart-meeting="meetingActions.handleRestartMeeting"
      @next-meeting="meetingActions.handleNextMeeting"
      @end-meeting="meetingActions.handleEndMeeting"
    />
  </div>
</template>
