import { ref, Ref } from "vue";
import api from "@/plugins/axios";

export interface Room {
  id: number;
  name: string;
  active_meeting_id: number;
  is_active: boolean
}

export type RoleEnum = "observer" | "voter";

interface ParticipantInfo {
  nickname: string;
  role: RoleEnum;
}

export interface Participant {
  [key: string]: ParticipantInfo
}

interface ApiError {
  response?: {
    data?: {
      message?: string;
    };
  };
}

export default function useRoom() {
  const currentRoom: Ref<Room | null> = ref(null);
  const roomList: Ref<Room[]> = ref([]);
  const participants: Ref<Participant> = ref({});
  const error: Ref<string | null> = ref(null);

  const fetchRoomList = async (): Promise<void> => {
    try {
      const { data } = await api.get<Room[]>("/room/list/");
      roomList.value = data;
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка загрузки списка комнат";
    }
  };

  const fetchRoomDetails = async (roomId: number): Promise<void> => {
    try {
      const { data } = await api.get<Room>(`/room/${roomId}/`);
      currentRoom.value = data;
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка загрузки комнаты";
    }
  };

  const fetchParticipants = async (roomId: number): Promise<void> => {
    try {
      const { data } = await api.get<{ participants: Participant }>(
        `/room/${roomId}/participants/`
      );
      participants.value = data.participants;
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка загрузки участников";
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
