<script setup>
import { ref, onBeforeMount, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import RoomHeader from "@/components/room/ui/RoomHeader.vue";
import WaitingMeetingState from "@/components/room/voting/states/WaitingMeetingState.vue";
import VotingMeetingState from "@/components/room/voting/states/VotingMeetingState.vue";
import ResultsMeetingState from "@/components/room/voting/states/ResultsMeetingState.vue";
import ParticipantsSection from "@/components/room/ui/ParticipantsSection.vue";

import useRoomState from "@/composables/room/useRoomState";
import useMeetingManager from "@/composables/room/useMeetingManager";
import useRoomWebSocketHandler from "@/composables/room/useRoomWebSocketHandler";
import useRoomParticipants from "@/composables/room/useRoomParticipants";
import { useRoomWebSocket } from "@/composables/api/useWebSocket";
import { useNotify } from '@/composables/useNotify.js'

import useRoom from "@/composables/api/useRoomAPI"

import useMeeting from "@/composables/api/useMeetingAPI";

const route = useRoute();
const router = useRouter();
const roomId = ref(route.params.room_id);

const roomName = ref("");

const notify = useNotify();

const { fetchRoomDetails, currentRoom } = useRoom()

const { roomState, ROOM_STATES, taskName, votes, resultsVotes, averageScore } =
  useRoomState();

const {
  participants,
  currentUser,
  fetchParticipants,
  getCurrentUser,
  userError,
} = useRoomParticipants(roomId.value);

const token = ref(localStorage.getItem("token"));

const userRole = ref("");

const redirectToLogin = () => router.push({ name: "Login" });

const { isConnected, connect, sendMessage, addMessageHandler } =
  useRoomWebSocket(
    `${import.meta.env.VITE_WS_BASE_URL}room/${roomId.value}/?token=${token.value}`
  );

const { currentMeeting } = useRoomWebSocketHandler(
  addMessageHandler,
  roomState,
  participants,
  votes,
  resultsVotes,
  averageScore,
  taskName,
  notify,
  redirectToLogin
);

const { meetingRoom } = useMeeting();

const { getRoomMeeting, ...meetingActions } = useMeetingManager(
  roomState,
  sendMessage,
  currentMeeting,
  notify
);

const handleVote = (voteValue) => {
  try {
    sendMessage({
      action: "submit_vote",
      vote: `${voteValue}`,
      token: token.value,
    });
  } catch (err) {
    notify.error("Произошла ошибка во время отправки голоса")
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
  } catch {
    redirectToLogin();
  }
  await fetchRoomDetails(roomId.value);
  roomName.value = currentRoom.value.name;

  await fetchParticipants();
});

onMounted(async () => {
  try {
    await connect();
  } catch (err) {
    console.error("Ошибка подключения:", err);
    notify.error("Ошибка подключения к WebSocket!")
  }
  if (currentMeeting.value == null) {
    const meeting = await getRoomMeeting(roomId.value);
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
  <div class="min-h-screen bg-base-200 flex flex-col items-center p-4 sm:p-6 gap-6">
    <RoomHeader
      :room-id="roomId"
      :task-name="taskName"
      :room-name="roomName"
      :is-connected="isConnected"
      :room-state="roomState"
      @leave-room="redirectToLogin"
    />

    <div v-if="roomState === ROOM_STATES.WAITING" class="w-full max-w-2xl">
      <WaitingMeetingState
        v-model:task-name="taskName"
        @start-voting="(taskName) => meetingActions.startVoting(roomId, taskName)"
      />
    </div>

    <div
      v-else-if="roomState === ROOM_STATES.VOTING && userRole === 'voter'"
      class="w-full max-w-md"
    >
      <VotingMeetingState
        @vote="handleVote"
        @update-task="meetingActions.updateMeetingTaskName"
      />
    </div>

    <div
      v-if="roomState !== ROOM_STATES.RESULTS"
      class="w-full max-w-3xl fixed bottom-10"
    >
      <ParticipantsSection
        :participants="participants"
        :votes="votes"
      />
    </div>

    <Transition
      appear
      enter-active-class="transition-all duration-700 ease-out"
      enter-from-class="opacity-0 translate-y-6"
      enter-to-class="opacity-100 translate-y-0"
    >
      <div
        v-if="roomState === ROOM_STATES.RESULTS"
        class="w-full max-w-3xl"
      >
        <ResultsMeetingState
          :results-votes="resultsVotes"
          :average-score="averageScore"
          @restart-meeting="meetingActions.handleRestartMeeting"
          @next-meeting="meetingActions.handleNextMeeting"
        />
      </div>    
    </Transition>
  </div>
</template>
