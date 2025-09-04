import { ref, Ref } from "vue";
import api from "@/plugins/axios";

interface UserVoteDetail {
  nickname: string;
  vote: number;
}

interface Vote {
  [key: string]: UserVoteDetail;
}

interface Meeting {
  id: number;
  room: string;
  task_name: string;
  votes: Vote[];
  average_score: number;
  active: boolean;
};

// Тип для ошибки
interface ApiError {
  response?: {
    data?: {
      message?: string;
    };
  };
};

export default function useRoom() {
  const meetingRoom: Ref<Meeting | null> = ref(null);
  const error: Ref<string | null> = ref(null);

  const createMeeting = async (roomId: string, taskName: string): Promise<Meeting | undefined> => {
    try {
      const { data } = await api.post<Meeting>("/meeting/", {
        room: roomId,
        task_name: taskName,
      });
      return data;
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка создания голосования";
    }
  };

  const getMeeting = async (meetingId: string): Promise<void> => {
    try {
      const { data } = await api.get<Meeting>(`/meeting/${meetingId}`);
      meetingRoom.value = data;
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка загрузки голосования";
    }
  };

  const endMeeting = async (meetingId: string): Promise<void> => {
    try {
      await api.put(`/meeting/${meetingId}/end`);
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка завершения голосования";
    }
  };

  const setMeetingTask = async (meetingId: string, task: string): Promise<void> => {
    try {
      await api.put(`/meeting/${meetingId}/task`, { task_name: task });
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка обновления задачи";
    }
  };

  const restartMeeting = async (meetingId: string): Promise<Meeting | undefined> => {
    try {
      const { data } = await api.put<Meeting>(`/meeting/${meetingId}/restart`);
      return data;
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка перезапуска комнаты";
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
