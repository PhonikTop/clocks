<script setup lang="ts">
import html2canvas from 'html2canvas-pro';
import { ref } from 'vue'

const captureArea = ref(null)
const screenshot = ref<null | string>(null)

const takeScreenshot = async () => {
  if (!captureArea.value) return

  try {
    const canvas = await html2canvas(captureArea.value, {
      logging: false,
      scale: 2,
      ignoreElements: (el) => el.classList.contains('no-screenshot')
    })

    screenshot.value = canvas.toDataURL('image/png')
  } catch (err) {
    console.error('Ошибка при создании скриншота:', err)
  }
}
const copyScreenshot = async () => {
  if (!screenshot.value) {
    return
  };

  try {
    const res = await fetch(screenshot.value)
    const blob = await res.blob()
    await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })])
  } catch (err) {
    console.error('Ошибка при копировании скрина:', err)
  }
}

const handleScreenshot = async() => {
  await takeScreenshot()
  await copyScreenshot()
  emit("resultsCopied");
}

const emit = defineEmits(["restartVoting", "nextVoting", "resultsCopied"]);
defineProps({
  resultsVotes: {
    type: Object,
    required: true,
  },
  averageScore: {
    type: [Number, null],
    default: null,
  },
  taskName: {
    type: String,
  },
});
</script>

<template>
  <div
    ref="captureArea"
    class="card bg-base-100 shadow p-6 space-y-6 max-w-2xl w-full mx-auto"
  >
    <div class="flex justify-between items-center">
      <div class="flex">
        <h2 class="text-xl font-semibold">
          Результаты голосования
        </h2>
        <button
          class="w-6 h-6 flex items-center justify-center text-black hover:text-gray-700 active:text-gray-900 transition-colors no-screenshot cursor-pointer"
          title="Скопировать"
          @click="handleScreenshot"
        >
          <svg
            class="w-4 h-4 translate-y-[3px]"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            fill="currentColor"
          >
            <path
              d="M4 2C2.895 2 2 2.895 2 4V18H4V4H18V2H4ZM8 6C6.895 6 6 6.895 6 8V20C6 21.105 6.895 22 8 22H20C21.105 22 22 21.105 22 20V8C22 6.895 21.105 6 20 6H8ZM8 8H20V20H8V8Z"
              stroke-linecap="round"
            />
          </svg>
        </button>
      </div>
      <h2 class="text-xl font-normal">
        {{ taskName }}
      </h2>
    </div>
    <div class="overflow-x-auto">
      <table class="table w-full">
        <thead>
          <tr>
            <th>Участник</th>
            <th class="text-right">
              Оценка
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(user, id) in resultsVotes"
            :key="id"
            class="hover:bg-base-200"
          >
            <td>{{ user.nickname }}</td>
            <td class="text-right">
              {{ user.vote }} ч.
            </td>
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

    <div class="flex flex-wrap gap-3 justify-end no-screenshot">
      <button
        class="btn btn-outline btn-warning"
        @click="$emit('restartVoting')"
      >
        Перезапустить
      </button>
      <button
        class="btn btn-primary"
        @click="$emit('nextVoting')"
      >
        Далее
      </button>
    </div>
  </div>
</template>
