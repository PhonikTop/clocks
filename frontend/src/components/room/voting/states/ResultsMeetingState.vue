<script setup>
defineEmits(["restartMeeting", "nextMeeting", "endMeeting"]);
defineProps({
  resultsVotes: {
    type: Object,
    required: true,
  },
  averageScore: {
    type: [Number, null],
    default: null,
  },
});
</script>

<template>
  <div class="card bg-base-100 shadow p-6 space-y-6 max-w-2xl w-full mx-auto">
    <h2 class="text-xl font-semibold">Результаты голосования</h2>

    <div class="overflow-x-auto">
      <table class="table w-full">
        <thead>
          <tr>
            <th>Участник</th>
            <th class="text-right">Оценка</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(user, id) in resultsVotes"
            :key="id"
            class="hover:bg-base-200"
          >
            <td>{{ user.nickname }}</td>
            <td class="text-right">{{ user.vote }} ч.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Среднее значение -->
    <div class="text-lg font-medium flex items-center gap-2">
      <span>Общая оценка:</span>
      <span class="badge badge-primary text-lg text-white p-3">
        {{ averageScore ?? "—" }} ч.
      </span>
    </div>

    <div class="flex flex-wrap gap-3 justify-end">
      <button class="btn btn-outline btn-warning" @click="$emit('restartMeeting')">
        Перезапустить
      </button>
      <button class="btn btn-primary" @click="$emit('nextMeeting')">
        Далее
      </button>
      <button class="btn btn-error text-white" @click="$emit('endMeeting')">
        Завершить
      </button>
    </div>
  </div>
</template>
