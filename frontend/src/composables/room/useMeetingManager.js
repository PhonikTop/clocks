import { ROOM_STATES } from "./useRoomState";
import useMeeting from "@/composables/api/useMeetingAPI";
import useRoom from "@/composables/api/useRoomAPI";

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
  roomState,
  sendMessage,
  currentMeeting,
  notify
) {
  const startVoting = async (roomId, taskName) => {
    try {
      roomState.value = ROOM_STATES.VOTING;
      await createMeeting(roomId, taskName);
    } catch (err) {
      notify.error("Произошла ошибка во время начала голосования")
      console.error("Ошибка начала голосования:", err);
      roomState.value = ROOM_STATES.WAITING;
    }
  };

  const getRoomMeeting = async (roomId) => {
    await fetchRoomDetails(roomId);
    if (currentRoom.value.active_meeting_id == null) return null;

    await getMeeting(currentRoom.value.active_meeting_id);

    return meetingRoom.value;
  };

  const updateMeetingTaskName = async (newName) => {
    if (!currentMeeting.value) return;
    await setMeetingTask(currentMeeting.value, newName);
  };

  const changeMeetingStatus = async (new_status) => {
    try {
      await sendMessage({
        action: "change_meeting_status",
        status: `${new_status}`,
      });
    } catch (err) {
      notify.error("Произошла ошибка во время статуса голосования")
      console.error("Ошибка изменения статуса голосования:", err);
    }
  };

  const handleRestartMeeting = () => {
    restartMeeting(currentMeeting.value);
    changeMeetingStatus("restart");
  };

  const handleNextMeeting = () => {
    changeMeetingStatus("next");
    localStorage.removeItem("active_meeting_id");
  };

  const handleEndMeeting = () => {
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
