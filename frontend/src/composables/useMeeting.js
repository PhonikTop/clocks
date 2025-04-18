import { ref } from "vue";
import api from "@/plugins/axios";

export default function useRoom() {
  const meetingRoom = ref(null);
  const error = ref(null);

  const createMeeting = async (roomId, taskName) => {
    try {
      const { data } = await api.post("/meeting/", {
        room: roomId,
        task_name: taskName,
      });
      return data;
    } catch (err) {
      error.value =
        err.response?.data?.message || "Ошибка создания голосования";
    }
  };

  const getMeeting = async (meetingId) => {
    try {
      const { data } = await api.get(`/meeting/${meetingId}/`);
      meetingRoom.value = data;
    } catch (err) {
      error.value =
        err.response?.data?.message || "Ошибка загрузки голосования";
    }
  };

  const endMeeting = async (meetingId) => {
    try {
      await api.post(`/meeting/${meetingId}/end`);
    } catch (err) {
      error.value =
        err.response?.data?.message || "Ошибка завершения голосования";
    }
  };

  const setMeetingTask = async (meetingId, task) => {
    try {
      await api.post(`/meeting/${meetingId}/task`, task);
    } catch (err) {
      error.value = err.response?.data?.message || "Ошибка обновления задачи";
    }
  };

  const restartMeeting = async (meetingId) => {
    try {
      const { data } = await api.post(`/meeting/${meetingId}/restart`);
      return data;
    } catch (err) {
      error.value = err.response?.data?.message || "Ошибка перезапуска комнаты";
    }
  };

  return {
    meetingRoom,
    error,
    createMeeting,
    getMeeting,
    endMeeting,
    setMeetingTask,
    restartMeeting,
  };
}
