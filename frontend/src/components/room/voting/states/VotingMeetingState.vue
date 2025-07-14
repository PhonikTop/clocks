<script setup>
import ChangeTaskForm from "@/components/room/voting/ui/ChangeTaskForm.vue";
import VotingForm from "@/components/room/voting/ui/VotingForm.vue";

defineProps({
  hasVoted: Boolean,
});

defineEmits(["vote", "update-task"]);
</script>

<template>
  <div class="flex flex-col gap-6">
    <ChangeTaskForm @submitted="$emit('update-task', $event)" />
    <VotingForm :disabled="hasVoted" @vote="$emit('vote', $event)" />
    <p v-if="hasVoted">Вы уже проголосовали!</p>
  </div>
</template>
