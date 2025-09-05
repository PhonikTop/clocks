import { ref, onMounted, Ref } from "vue";
import { ROOM_STATES } from "./useRoomState";
import useMeeting, { Vote } from "@/composables/api/useMeetingAPI";
import { Participant } from "../api/useRoomAPI";
import { User } from "../api/useUserAPI";
import { useNotify } from "../useNotify";

const { getMeeting, meetingRoom } = useMeeting();

interface UserJoinedMsg {
  user: Record<string, { nickname: string }>;
}

interface VotedMsg {
  user: string;
}

interface UserOnlineStatusMsg {
  user: Record<string, { nickname: string }>;
}

interface TaskNameChangedMsg {
  new_task_name?: string;
  user: string;
}

interface ResultsMsg {
  votes: Vote[];
  average_score: number;
}

interface UserKickedMsg {
  kicked: Record<string, User>;
  kicker: Record<string, User>;
}

interface MeetingStartedMsg {
  id: number;
}

interface VotedUsersMsg {
  voted_users: string[]
}

interface MeetingStatusChangeMsg {
  status?: "restart" | "next";
}

interface WebsocketMessages {
  "user_joined": UserJoinedMsg;
  "user_voted": VotedMsg;
  "user_online": UserOnlineStatusMsg;
  "user_offline": UserOnlineStatusMsg;
  "task_name_changed": TaskNameChangedMsg;
  "results": ResultsMsg;
  "user_kicked": UserKickedMsg;
  "meeting_started": MeetingStartedMsg;
  "voted_users_update": VotedUsersMsg;
  "meeting_change_status": MeetingStatusChangeMsg;
}

type AddMessageHandler = <K extends keyof WebsocketMessages>(
  type: K,
  handler: (msg: WebsocketMessages[K]) => void
) => void;

export default function useRoomWebSocketHandler(
  addMessageHandler: AddMessageHandler,
  roomState: Ref<string>,
  participants: Ref<Participant>,
  votes: Ref<string[]>,
  resultsVotes: Ref<Vote[]>,
  averageScore: Ref<number | null>,
  taskName: Ref<string | null>,
  notify: ReturnType<typeof useNotify>,
  redirectToLogin: () => void,
  userUuid: Ref<string>,
  hasVoted: Ref<boolean>
) {
  const currentMeeting: Ref<null | number> = ref(null);

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
      const userId: string = Object.keys(msg.user)[0];

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
      localStorage.setItem("hasVoted", JSON.stringify(false));
      hasVoted.value = false;
    });

    addMessageHandler("task_name_changed", (msg) => {
      if (!msg?.new_task_name) return;
      taskName.value = msg.new_task_name;
      notify.info(`Описание задачи было измененно участником ${msg.user}`);
    });

    addMessageHandler("user_kicked", (msg) => {
      const kickerId = Object.keys(msg.kicker)[0];
      const kickerNickname = msg.kicker[kickerId].nickname;

      const kickedId: string = Object.keys(msg.kicked)[0];
      const kickedNickname = msg.kicked[kickedId].nickname;

      delete participants.value[kickedId];

      notify.info(`Участник ${kickerNickname} кикнул участника ${kickedNickname}`)

      if (kickedId === userUuid.value) {redirectToLogin()}
    });

    addMessageHandler("meeting_started", (msg) => {
      if (!msg?.id) return;
      getMeeting(msg.id)
        .then(() => {
          currentMeeting.value = msg.id;
          localStorage.setItem("hasVoted", JSON.stringify(false));
          hasVoted.value = false;
          localStorage.setItem("active_meeting_id", msg.id.toString());
          taskName.value = meetingRoom.value?.task_name || "";
          roomState.value = ROOM_STATES.VOTING;
        })
        .catch(console.error);
    });

    addMessageHandler("voted_users_update", (msg) => {
      if (!msg?.voted_users) return;
      votes.value = msg.voted_users;
    });

    addMessageHandler("meeting_change_status", (msg) => {
      if (!msg?.status) return;

      switch (msg.status) {
        case "restart":
          hasVoted.value = false;
          roomState.value = ROOM_STATES.VOTING;
          votes.value = [];
          notify.info("Голосование перезапущенно")
          break;
        case "next":
          roomState.value = ROOM_STATES.WAITING;
          currentMeeting.value = null;
          votes.value = [];
          localStorage.removeItem("active_meeting_id");
          taskName.value = null;
          break;
      }
    });
  };

  onMounted(setupHandlers);
  return {
    currentMeeting,
  };
}
