<script setup>
import ChangeTaskForm from "@/components/room/voting/ui/ChangeTaskForm.vue";
import VotingForm from "@/components/room/voting/ui/VotingForm.vue";

defineProps({
  hasVoted: Boolean,
  userRole: String
});

defineEmits(["vote", "update-task"]);
</script>

<template>
  <div class="flex flex-col items-center gap-6">
    <ChangeTaskForm @submitted="$emit('update-task', $event)" class="w-full"/>
    <VotingForm v-if="!hasVoted & userRole === `voter`" @vote="$emit('vote', $event)" />
  </div>
</template>
