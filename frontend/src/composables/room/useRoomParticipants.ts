import { computed } from "vue";
import useRoom from "@/composables/api/useRoomAPI";
import useUser from "@/composables/api/useUserAPI";

export default function useRoomParticipants(roomId: number) {
  const { participants, fetchParticipants: fetchRoomParticipants } = useRoom();

  const userComposable = useUser();
  const {
    currentUser,
    error: userError,
    getCurrentUser: fetchCurrentUser,
    kickUser,
  } = userComposable;

  const currentUserId = computed(() => currentUser.value?.user_uuid || "");

  const fetchParticipants = async () => {
    await fetchRoomParticipants(roomId);
  };

  const getCurrentUser = async () => {
    await fetchCurrentUser(roomId);
  };

  const kickUserRoom = async (kickUserUuid: string) => {
    await kickUser(roomId, kickUserUuid);
  }

  return {
    participants,
    currentUser,
    userError,
    currentUserId,
    fetchParticipants,
    getCurrentUser,
    kickUserRoom
  };
}
