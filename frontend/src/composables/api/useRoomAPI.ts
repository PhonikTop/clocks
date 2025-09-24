import { ref, Ref } from "vue";
import api from "@/plugins/axios";
import { useTimertStore } from "@/stores/roomTimer";

const timer = useTimertStore() 

export interface Room {
  id: number;
  name: string;
  active_meeting_id: number;
  is_active: boolean
}

export type RoleEnum = "observer" | "voter";

export interface ParticipantInfo {
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

  const startRoomTimer = async (roomId: number, minutes: number): Promise<void> => {
    try {
      await api.post<null>(`/room/${roomId}/timer_start/`, {
        minutes: minutes
      });
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка создания таймера";
    }
  };

  const resetRoomTimer = async (roomId: number): Promise<void> => {
    try {
      await api.delete<null>(`/room/${roomId}/reset_timer/`);
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка сброса таймера";
    }
  };

  const fetchRoomTimer = async (roomId: number): Promise<void> => {
    try {
      const { data } = await api.get<{"timer_end_time": number | null}>(
        `/room/${roomId}/get_timer/`
      );
      if (data.timer_end_time !== null) {
        timer.updateTime(data.timer_end_time * 1000)
      }
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка загрузки таймера";
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
    startRoomTimer,
    resetRoomTimer,
    fetchRoomTimer
  };
}
