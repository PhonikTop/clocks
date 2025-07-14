import { computed } from "vue";
import useRoom from "@/composables/api/useRoomAPI";
import useUser from "@/composables/api/useUserAPI";

export default function useRoomParticipants(roomId) {
  const { participants, fetchParticipants: fetchRoomParticipants } = useRoom();

  const userComposable = useUser();
  const {
    currentUser,
    error: userError,
    getCurrentUser: fetchCurrentUser,
  } = userComposable;

  const currentUserId = computed(() => currentUser.value?.user_uuid || "");

  const fetchParticipants = async () => {
    await fetchRoomParticipants(roomId);
  };

  const getCurrentUser = async () => {
    const token = localStorage.getItem("token");
    await fetchCurrentUser(roomId, token);
  };

  return {
    participants,
    currentUser,
    userError,
    currentUserId,
    fetchParticipants,
    getCurrentUser,
  };
}
