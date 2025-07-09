<script setup>
import VotersList from "@/components/room/ui/VotersList.vue";
import ObserversList from "@/components/room/ui/ObserversList.vue";

defineProps({
  participants: Object,
  votes: Array,
});
</script>

<template>
  <div class="participants-section">
    <VotersList :participants="participants" :votes="votes" />
    <ObserversList :participants="participants" />
  </div>
</template>
