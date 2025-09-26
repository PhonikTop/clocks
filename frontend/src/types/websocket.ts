import { Vote } from "@/composables/api/useMeetingAPI";
import { User } from "@/composables/api/useUserAPI";

export interface UserJoinedMsg {
  user: Record<string, { nickname: string }>;
}

export interface VotedMsg {
  user: string;
}

export interface UserOnlineStatusMsg {
  user: Record<string, { nickname: string }>;
}

export interface TaskNameChangedMsg {
  new_task_name?: string;
  user: string;
}

export interface ResultsMsg {
  votes: Vote[];
  average_score: number;
}

export interface UserKickedMsg {
  kicked: Record<string, User>;
  kicker: Record<string, User>;
}

export interface RoomTimerStarted {
  "end_time": number,
  "timer_started_user": Record<string, User>,
}

export interface RoomTimerReset {
  "timer_reset_user": Record<string, User>,
}

export interface MeetingStartedMsg {
  id: number;
}

export interface VotedUsersMsg {
  voted_users: string[]
}

export interface MeetingStatusChangeMsg {
  status?: "restart" | "next";
}

export interface WebsocketMessages {
  "user_joined": UserJoinedMsg;
  "user_voted": VotedMsg;
  "user_online": UserOnlineStatusMsg;
  "user_offline": UserOnlineStatusMsg;
  "task_name_changed": TaskNameChangedMsg;
  "results": ResultsMsg;
  "user_kicked": UserKickedMsg;
  "timer_started": RoomTimerStarted;
  "timer_reset": RoomTimerReset;
  "meeting_started": MeetingStartedMsg;
  "voted_users_update": VotedUsersMsg;
  "voting_change_status": MeetingStatusChangeMsg;
}

export type AddMessageHandler = <K extends keyof WebsocketMessages>(
  type: K,
  handler: (msg: WebsocketMessages[K]) => void
) => void;
