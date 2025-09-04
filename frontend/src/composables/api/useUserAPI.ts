import { ref, Ref } from "vue";
import api from "@/plugins/axios";

interface User {
  nickname: string;
  role: string;
}

interface JoinResponse {
  token: string;
}

interface ApiError {
  response?: {
    data?: {
      message?: string;
    };
    status?: number;
  };
}

export default function useRoom() {
  const currentUser: Ref<User | null> = ref(null);
  const error: Ref<string | null> = ref(null);

  const getCurrentUser = async (roomId: number): Promise<void> => {
    try {
      const { data } = await api.get<User>(`/user/${roomId}/`);
      currentUser.value = data;
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка загрузки пользователя";
    }
  };

  const joinRoom = async (
    roomId: number,
    nickname: string,
    role: string
  ): Promise<void> => {
    try {
      const { data } = await api.post<JoinResponse>(`/user/join/${roomId}/`, {
        nickname,
        role,
      });
      localStorage.setItem("token", data.token);
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка при входе в комнату";
    }
  };

  const kickUser = async (roomId: number, kickUserUuid: string): Promise<void> => {
    try {
      await api.post(`/user/${roomId}/kick`, {
        user_uuid: kickUserUuid,
      });
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка при кике пользователя";
    }
  };

  return {
    currentUser,
    error,
    getCurrentUser,
    joinRoom,
    kickUser,
  };
}
