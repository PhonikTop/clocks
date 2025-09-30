import { ROOM_STATES } from "./useRoomState";
import useVoting from "@/composables/api/useVotingsAPI";
import useRoom from "@/composables/api/useRoomAPI";
import { Ref } from "vue";
import { useNotify } from "@/composables/useNotify";
import { WebSocketSendMessage } from "@/composables/api/useWebSocket";

const {
  createVoting,
  setVotingTask,
  restartVoting,
  endVoting,
  getVoting,
  roomVoting,
} = useVoting();

const { fetchRoomDetails, currentRoom } = useRoom();

export default function useVotingManager(
  roomState: Ref<ROOM_STATES>,
  sendMessage: (msg: WebSocketSendMessage) => void,
  currentVoting: Ref<number | null>,
  notify: ReturnType<typeof useNotify>
) {
  const startVoting = async (roomId: number, taskName: string) => {
    try {
      roomState.value = ROOM_STATES.VOTING;
      await createVoting(roomId, taskName);
    } catch (err) {
      notify.error("Произошла ошибка во время начала голосования")
      console.error("Ошибка начала голосования:", err);
      roomState.value = ROOM_STATES.WAITING;
    }
  };

  const getRoomVoting = async (roomId: number) => {
    await fetchRoomDetails(roomId);
    if (currentRoom.value?.active_voting_id == null) return null;

    await getVoting(currentRoom.value.active_voting_id);

    return roomVoting.value;
  };

  const updateVotingTaskName = async (newName: string) => {
    if (!currentVoting.value) return;
    await setVotingTask(currentVoting.value, newName);
  };

  const changeVotingStatus = (newStatus: string) => {
    try {
      sendMessage({
        action: "change_voting_status",
        status: newStatus,
      });
    } catch (err) {
      notify.error("Произошла ошибка во время изменения статуса голосования")
      console.error("Ошибка изменения статуса голосования:", err);
    }
  };

  const handleRestartVoting = () => {
    if (!currentVoting.value) {return;}
    restartVoting(currentVoting.value);
  };

  const handleNextVoting = () => {
    changeVotingStatus("next");
    localStorage.removeItem("active_Voting_id");
  };

  const handleEndVoting = () => {
    if (!currentVoting.value) {return;}
    endVoting(currentVoting.value);
    changeVotingStatus("ended");
    localStorage.removeItem("active_Voting_id");
  };

  return {
    startVoting,
    getRoomVoting,
    updateVotingTaskName,
    handleRestartVoting,
    handleNextVoting,
    handleEndVoting,
  };
}
