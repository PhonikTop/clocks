<script setup>
import ChangeTaskForm from "@/components/room/voting/ui/ChangeTaskForm.vue";
import VotingForm from "@/components/room/voting/ui/VotingForm.vue";

defineProps({
  hasVoted: Boolean,
});

defineEmits(["vote", "update-task"]);
</script>

<template>
  <div class="voting-state">
    <ChangeTaskForm @room-name-updated="$emit('update-task', $event)" />
    <VotingForm :disabled="hasVoted" @vote="$emit('vote', $event)" />
    <p v-if="hasVoted">Вы уже проголосовали!</p>
  </div>
</template>
