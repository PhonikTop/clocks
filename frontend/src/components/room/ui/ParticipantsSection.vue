<script setup lang="ts">
import VotersList from "@/components/room/ui/VotersList.vue";
import ObserversList from "@/components/room/ui/ObserversList.vue";
import { Participant } from "@/composables/api/useRoomAPI";

const props = defineProps<{
  participants: Participant
  votes: string[]
}>()
const emit = defineEmits(["kick-user"]);
</script>

<template>
  <div class="flex flex-col sm:p-6 gap-6">
    <VotersList
      :participants="props.participants" 
      :votes="props.votes"
      @kick-user="(voterId: string) => emit('kick-user', voterId)"
    />
    <ObserversList :participants="props.participants" />
  </div>
</template>
