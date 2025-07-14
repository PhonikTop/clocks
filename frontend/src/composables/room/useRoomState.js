import { ref } from "vue";

export const ROOM_STATES = {
  WAITING: "waiting",
  VOTING: "voting",
  RESULTS: "results",
};

export default function useRoomState() {
  const roomState = ref(ROOM_STATES.WAITING);
  const taskName = ref("");
  const votes = ref([]);
  const resultsVotes = ref({});
  const averageScore = ref(null);

  return {
    roomState,
    taskName,
    votes,
    resultsVotes,
    averageScore,
    ROOM_STATES,
  };
}
