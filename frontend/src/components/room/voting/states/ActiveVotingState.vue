<script setup lang="ts">
import ChangeTaskForm from "@/components/room/voting/ui/ChangeTaskForm.vue";
import VotingForm from "@/components/room/voting/ui/VotingForm.vue";

defineProps({
  userRole: String,
  showKeyboard: Boolean
});

defineEmits(["vote", "update-task", "change-input-type"]);
</script>

<template>
  <div class="flex flex-col items-center gap-6">
    <ChangeTaskForm
      class="w-full"
      @submitted="$emit('update-task', $event)"
    />
    <VotingForm
      v-if="showKeyboard && userRole === `voter`"
      @vote="$emit('vote', $event)"
      @change-input-type="$emit('change-input-type', $event)"
    />
  </div>
</template>
