import { ref } from "vue";
import api from "@/plugins/axios";

export default function useRoom() {
  const currentUser = ref(null);
  const error = ref(null);

  const getCurrentUser = async (roomId) => {
    try {
      const { data } = await api.get(`/user/${roomId}/`);
      currentUser.value = data;
    } catch (err) {
      error.value = err.response;
    }
  };

  const joinRoom = async (roomId, nickname, role) => {
    try {
      const { data } = await api.post(`/user/join/${roomId}/`, {
        nickname: nickname,
        role: role,
      });
      localStorage.setItem("token", data.token);
    } catch (err) {
      error.value = err.response;
    }
  };

  return {
    currentUser,
    error,
    getCurrentUser,
    joinRoom,
  };
}
