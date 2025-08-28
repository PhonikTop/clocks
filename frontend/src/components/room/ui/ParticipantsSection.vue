<script setup>
import VotersList from "@/components/room/ui/VotersList.vue";
import ObserversList from "@/components/room/ui/ObserversList.vue";

defineProps({
  participants: Object,
  votes: Array,
});
const emit = defineEmits(["kick-user"]);
</script>

<template>
  <div class="flex flex-col sm:p-6 gap-6">
    <VotersList
      :participants="participants" 
      :votes="votes"
      @kick-user="(voterId) => emit('kick-user', voterId)"
    />
    <ObserversList :participants="participants"/>
  </div>
</template>
