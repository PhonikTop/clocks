import { ref } from "vue";
import api from "@/plugins/axios";

export default function useRoom() {
  const currentRoom = ref(null);
  const roomList = ref([]);
  const participants = ref([]);
  const error = ref(null);

  const fetchRoomList = async () => {
    try {
      const { data } = await api.get("/room/list/");
      roomList.value = data;
    } catch (err) {
      error.value =
        err.response?.data?.message || "Ошибка загрузки списка комнат";
    }
  };

  const fetchRoomDetails = async (roomId) => {
    try {
      const { data } = await api.get(`/room/${roomId}/`);
      currentRoom.value = data;
    } catch (err) {
      error.value = err.response?.data?.message || "Ошибка загрузки комнаты";
    }
  };

  const fetchParticipants = async (roomId) => {
    try {
      const { data } = await api.get(`/room/${roomId}/participants/`);
      participants.value = data.participants;
    } catch (err) {
      error.value = err.response?.data?.message || "Ошибка загрузки участников";
    }
  };

  return {
    currentRoom,
    roomList,
    participants,
    error,
    fetchRoomList,
    fetchRoomDetails,
    fetchParticipants,
  };
}
