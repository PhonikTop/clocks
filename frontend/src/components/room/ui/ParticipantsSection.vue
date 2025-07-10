<script setup>
import VotersList from "@/components/room/ui/VotersList.vue";
import ObserversList from "@/components/room/ui/ObserversList.vue";

defineProps({
  participants: Object,
  votes: Array,
});
</script>

<template>
  <div class="flex flex-col sm:p-6 gap-6">
    <VotersList :participants="participants" :votes="votes" />
    <ObserversList :participants="participants" />
  </div>
</template>
