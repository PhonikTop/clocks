import { ref, Ref } from "vue";
import api from "@/plugins/axios";

interface UserVoteDetail {
  nickname: string;
  vote: number;
}

export interface Vote {
  [key: string]: UserVoteDetail;
}

export interface Voting {
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

export default function useVoting() {
  const roomVoting: Ref<Voting | null> = ref(null);
  const error: Ref<string | null> = ref(null);

  const createVoting = async (roomId: number, taskName: string): Promise<Voting | undefined> => {
    try {
      const { data } = await api.post<Voting>("/voting/", {
        room: roomId,
        task_name: taskName,
      });
      return data;
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка создания голосования";
    }
  };

  const getVoting = async (votingId: number): Promise<void> => {
    try {
      const { data } = await api.get<Voting>(`/voting/${votingId}`);
      roomVoting.value = data;
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка загрузки голосования";
    }
  };

  const endVoting = async (votingId: number): Promise<void> => {
    try {
      await api.put(`/voting/${votingId}/end`);
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка завершения голосования";
    }
  };

  const setVotingTask = async (votingId: number, task: string): Promise<void> => {
    try {
      await api.put(`/voting/${votingId}/task`, { task_name: task });
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка обновления задачи";
    }
  };

  const restartVoting = async (votingId: number): Promise<Voting | undefined> => {
    try {
      const { data } = await api.put<Voting>(`/voting/${votingId}/restart`);
      return data;
    } catch (err: unknown) {
      const e = err as ApiError;
      error.value = e.response?.data?.message || "Ошибка перезапуска комнаты";
    }
  };

  return {
    roomVoting,
    error,
    createVoting,
    getVoting,
    endVoting,
    setVotingTask,
    restartVoting,
  };
}
