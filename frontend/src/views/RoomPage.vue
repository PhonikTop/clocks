<script setup lang="ts">
import { ref, onBeforeMount, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import RoomHeader from "@/components/room/ui/RoomHeader.vue";
import WaitingVotingState from "@/components/room/voting/states/WaitingVotingState.vue";
import ActiveVotingState from "@/components/room/voting/states/ActiveVotingState.vue";
import ResultsVotingState from "@/components/room/voting/states/ResultsVotingState.vue";
import ParticipantsSection from "@/components/room/ui/ParticipantsSection.vue";

import useRoomState from "@/composables/room/useRoomState";
import useVotingManager from "@/composables/room/useVotingManager";
import useRoomWebSocketHandler from "@/composables/room/useRoomWebSocketHandler";
import useRoomParticipants from "@/composables/room/useRoomParticipants";
import { useRoomWebSocket } from "@/composables/api/useWebSocket";
import { useNotify } from '@/composables/useNotify.js'
import { useTimerStore } from "@/stores/roomTimer";

import useRoom from "@/composables/api/useRoomAPI"


const route = useRoute();
const router = useRouter();
const roomId = ref(Number(route.params.room_id));

const roomName = ref("");

const notify = useNotify();
const timer = useTimerStore()

const { fetchRoomDetails, currentRoom, startRoomTimer, fetchRoomTimer, resetRoomTimer } = useRoom()

const { roomState, ROOM_STATES, taskName, votes, resultsVotes, averageScore } =
  useRoomState();

const {
  participants,
  currentUser,
  fetchParticipants,
  getCurrentUser,
  userError,
  kickUserRoom
} = useRoomParticipants(roomId.value);

const token = ref(localStorage.getItem("token"));

const userRole = ref("");
const userUuid = ref("")

const hasVoted = ref(false)

const redirectToLogin = () => router.push({ name: "Login" });

const { isConnected, connect, sendMessage, addMessageHandler } =
  useRoomWebSocket(
    `ws/${roomId.value}/?token=${token.value}`
  );

const { currentVoting } = useRoomWebSocketHandler(
  addMessageHandler,
  roomState,
  participants,
  votes,
  resultsVotes,
  averageScore,
  taskName,
  notify,
  redirectToLogin,
  userUuid,
  hasVoted
);

const { getRoomVoting, ...votingActions } = useVotingManager(
  roomState,
  sendMessage,
  currentVoting,
  notify,
);

const handleVote = (voteValue: number) => {
  try {
    hasVoted.value = true;
    localStorage.setItem("hasVoted", JSON.stringify(true))
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

const handleKickUser = async (voterId: string) => {
  await kickUserRoom(voterId)
}

const handleRestartRoomTimer = async () => {
  await resetRoomTimer(roomId.value)
}

onBeforeMount(async () => {
  if (!token.value) redirectToLogin();

  try {
    await getCurrentUser();
    if (userError.value?.status === 403) {
      redirectToLogin();
      return;
    }
    if (currentUser.value) {
      userRole.value = currentUser.value.role;
      userUuid.value = currentUser.value.user_uuid;
    }
  } catch {
    redirectToLogin();
  }
  await fetchRoomDetails(roomId.value);

  if (currentRoom.value) {
    roomName.value = currentRoom.value.name;
  }

  hasVoted.value = JSON.parse(localStorage.getItem("hasVoted") ?? "false");

  await fetchParticipants();
  await fetchRoomTimer(roomId.value)
});

onMounted(async () => {
  try {
    await connect();
  } catch (err) {
    console.error("Ошибка подключения:", err);
    notify.error("Ошибка подключения к WebSocket!")
  }
  if (currentVoting.value == null) {
    const voting = await getRoomVoting(roomId.value);
    if (voting?.id != null) {
      currentVoting.value = voting.id;
      localStorage.setItem("active_voting_id", JSON.stringify(voting.id));
      taskName.value = voting.task_name;
      roomState.value = ROOM_STATES.VOTING;
    }
  }
});
</script>

<template>
  <div class="min-h-screen bg-base-200 flex flex-col p-4 sm:p-6 gap-6">
    <RoomHeader
      :room-id="roomId"
      :task-name="taskName"
      :room-name="roomName"
      :is-connected="isConnected"
      :room-state="roomState"
      :end-timestamp="timer.timeEndTS"
      @reset-timer="handleRestartRoomTimer"
      @leave-room="redirectToLogin"
      @restart-voting="votingActions.handleRestartVoting"
      @start-timer="(minutes: number) => startRoomTimer(roomId, minutes)"
    />

    <div class="flex flex-1 w-full gap-6 flex-col md:flex-row">
      <div class="flex-1 flex flex-col items-center gap-6">
        <div
          v-if="roomState === ROOM_STATES.WAITING"
          class="w-full max-w-2xl"
        >
          <WaitingVotingState
            v-model:task-name="taskName"
            @start-voting="(taskName: string) => votingActions.startVoting(roomId, taskName)"
          />
        </div>

        <div
          v-else-if="roomState === ROOM_STATES.VOTING"
          class="w-full max-w-2xl"
        >
          <ActiveVotingState
            :user-role="userRole"
            :has-voted="hasVoted"
            @vote="handleVote"
            @update-task="votingActions.updateVotingTaskName"
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
            <ResultsVotingState
              :results-votes="resultsVotes"
              :average-score="averageScore"
              :task-name="taskName"
              @restart-voting="votingActions.handleRestartVoting"
              @next-voting="votingActions.handleNextVoting"
              @results-copied="notify.info(`Результаты были успешно скопированы`)"
            />
          </div>
        </Transition>
      </div>

      <div
        v-if="roomState !== ROOM_STATES.RESULTS"
        class="w-full md:w-84"
      >
        <ParticipantsSection
          :participants="participants"
          :votes="votes"
          @kick-user="handleKickUser"
        />
      </div>
    </div>
  </div>
</template>
