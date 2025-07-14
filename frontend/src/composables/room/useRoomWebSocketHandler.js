import { ref, onMounted } from "vue";
import { ROOM_STATES } from "./useRoomState";
import useMeeting from "@/composables/api/useMeetingAPI";

const { getMeeting, meetingRoom } = useMeeting();

export default function useRoomWebSocketHandler(
  addMessageHandler,
  roomState,
  participants,
  votes,
  resultsVotes,
  averageScore,
  taskName,
  notify,
  redirectToLogin
) {
  const currentMeeting = ref(null);

  const setupHandlers = () => {
    addMessageHandler("user_joined", (msg) => {
      if (!msg?.user) return;
      Object.assign(participants.value, msg.user);
    });

    addMessageHandler("user_voted", (msg) => {
      if (!msg?.user) return;
      if (!votes.value.includes(msg.user)) {
        votes.value.push(msg.user);
      }
    });

    addMessageHandler("user_online", (msg) => {
      if (!msg?.user) return;
      const userId = Object.keys(msg.user)[0];

      if (!participants.value[userId]) {
        Object.assign(participants.value, msg.user);
      }
    });

    addMessageHandler("user_offline", (msg) => {
      if (!msg?.user) return;
      const userId = Object.keys(msg.user)[0];

      if (participants.value[userId]) {
        delete participants.value[userId];
      }
    });

    addMessageHandler("results", (msg) => {
      if (!msg?.votes || !msg?.average_score) return;
      roomState.value = ROOM_STATES.RESULTS;
      resultsVotes.value = msg.votes;
      averageScore.value = msg.average_score;
    });

    addMessageHandler("task_name_changed", (msg) => {
      if (!msg?.new_task_name) return;
      taskName.value = msg.new_task_name;
      notify.info("Описание задачи было измененно")
    });

    addMessageHandler("meeting_started", async (msg) => {
      if (!msg?.id) return;
      await getMeeting(msg.id);
      currentMeeting.value = msg.id;
      localStorage.setItem("active_meeting_id", msg.id);
      taskName.value = meetingRoom.value.task_name;

      roomState.value = ROOM_STATES.VOTING;
    });

    addMessageHandler("voted_users_update", (msg) => {
      if (!msg?.voted_users) return;
      votes.value = msg.voted_users;
    });

    addMessageHandler("meeting_change_status", (msg) => {
      if (!msg?.status) return;

      switch (msg.status) {
        case "restart":
          roomState.value = ROOM_STATES.VOTING;
          votes.value = [];
          break;
        case "next":
          roomState.value = ROOM_STATES.WAITING;
          currentMeeting.value = null;
          votes.value = [];
          localStorage.removeItem("active_meeting_id");
          taskName.value = null;
          break;
        case "ended":
          redirectToLogin();
          break;
      }
    });
  };

  onMounted(setupHandlers);
  return {
    currentMeeting,
  };
}
