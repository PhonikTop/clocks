import { ROOM_STATES } from "./useRoomState";
import useMeeting from "@/composables/api/useMeetingAPI";
import useRoom from "@/composables/api/useRoomAPI";
import { Ref } from "vue";
import { useNotify } from "@/composables/useNotify";

const {
  createMeeting,
  setMeetingTask,
  restartMeeting,
  endMeeting,
  getMeeting,
  meetingRoom,
} = useMeeting();

const { fetchRoomDetails, currentRoom } = useRoom();

export default function useMeetingManager(
  roomState: Ref<ROOM_STATES>,
  sendMessage: (msg: unknown) => void,
  currentMeeting: Ref<number | null>,
  notify: ReturnType<typeof useNotify>
) {
  const startVoting = async (roomId: number, taskName: string) => {
    try {
      roomState.value = ROOM_STATES.VOTING;
      await createMeeting(roomId, taskName);
    } catch (err) {
      notify.error("Произошла ошибка во время начала голосования")
      console.error("Ошибка начала голосования:", err);
      roomState.value = ROOM_STATES.WAITING;
    }
  };

  const getRoomMeeting = async (roomId: number) => {
    await fetchRoomDetails(roomId);
    if (currentRoom.value?.active_meeting_id == null) return null;

    await getMeeting(currentRoom.value.active_meeting_id);

    return meetingRoom.value;
  };

  const updateMeetingTaskName = async (newName: string) => {
    if (!currentMeeting.value) return;
    await setMeetingTask(currentMeeting.value, newName);
  };

  const changeMeetingStatus = (newStatus: string) => {
    try {
      sendMessage({
        action: "change_meeting_status",
        status: newStatus,
      });
    } catch (err) {
      notify.error("Произошла ошибка во время изменения статуса голосования")
      console.error("Ошибка изменения статуса голосования:", err);
    }
  };

  const handleRestartMeeting = () => {
    if (!currentMeeting.value) {return;}
    restartMeeting(currentMeeting.value);
  };

  const handleNextMeeting = () => {
    changeMeetingStatus("next");
    localStorage.removeItem("active_meeting_id");
  };

  const handleEndMeeting = () => {
    if (!currentMeeting.value) {return;}
    endMeeting(currentMeeting.value);
    changeMeetingStatus("ended");
    localStorage.removeItem("active_meeting_id");
  };

  return {
    startVoting,
    getRoomMeeting,
    updateMeetingTaskName,
    handleRestartMeeting,
    handleNextMeeting,
    handleEndMeeting,
    meetingRoom,
  };
}
