<template>
  <div class="flex min-w-0 flex-col">
    <div class="flex gap-[15px] p-5 overflow-x-auto flex-nowrap">
      <button
        v-for="(cardNumber, index) in cardPack" 
        :key="index"
        :class="[
          'relative w-[137px] h-[198px] lg:w-[156px] lg:h-[209px] flex-shrink-0 bg-white rounded-[22px] first:ml-0 -ml-[85px] lg:ml-0 flex items-center justify-center font-sans text-[#333] text-7xl lg:text-4xl transition-all duration-300',
          
          selectedCardIndex === index
            ? 'z-20 -translate-y-4 shadow-xl border-2 border-blue-500' 
            : 'border border-gray-200 shadow-sm hover:-translate-y-1'
        ]"
        @click="handleVote(index)"
      >
        <span class="absolute top-3 left-4 text-base lg:text-3xl font-semibold text-gray-400 lg:hidden select-none">
          {{ cardNumber }}
        </span>
        {{ cardNumber }}
      </button>
    </div>
    <div class="flex flex-row justify-center">
      <button
        command="show-modal"
        commandfor="dialog"
        class="btn"
      >
        Сменить колоду
      </button>
      <button
        class="btn"
        @click="handleChangeInputType"
      >
        Сменить тип ввода
      </button>
    </div>
  </div>

  <dialog
    id="dialog"
    class="modal"
  >
    <div class="modal-box">
      <h3 class="text-lg font-bold">
        Сменить набор колоды
      </h3>
      <div class="flex flex-col justify-center">
        <div class="mt-5 grid grid-cols-5 gap-3">
          <input
            v-for="(_, cardNumber) in 10" 
            :key="cardNumber"
            v-model.number="editingCardPack[cardNumber]"
            type="text"
            maxlength="2" 
            inputmode="numeric"
            pattern="^[1-9]\d?$" 
            placeholder="—"
            class="aspect-[2/3] rounded-xl border-2 border-gray-200 bg-gray-50 text-center text-xl font-bold text-gray-800 outline-none transition-all placeholder:text-gray-300 hover:border-gray-300 focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-100"
            >                      
        </div>
        <div class="join mx-auto mt-5 w-full max-w-xs">
          <input
            v-model="quickCardPackInput"
            type="text"
            class="input join-item"
            placeholder="1;2;5;10;..."
          >
          <button 
            class="btn btn-square join-item"
            @click="handleQucikChangeCardPack"
          >
            <svg
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="2.5"
              stroke="currentColor"
              class="size-[1.2em]"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3"
              />
            </svg>
          </button>
        </div>
      </div>
      <div class="modal-action">
        <form method="dialog">
          <div class="flex gap-2">
            <button class="btn">
              Отмена
            </button>
            <button
              class="btn btn-primary"
              :disabled="!isValidCards(editingCardPack)"
              @click="handleChangeCardPack"
            >
              Подтвердить
            </button>
          </div>
        </form>
      </div>
    </div>
    <form
      method="dialog"
      class="modal-backdrop"
    >
      <button class="!cursor-auto">
        close
      </button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { InputType } from '@/types/inputType'
import { ref } from 'vue'

const emit = defineEmits(["vote", "change-input-type"])

const selectedCardIndex = ref()

const cardPack = ref([1,2,3,4,5,6,7,8,9,10])

const editingCardPack = ref([...cardPack.value])

const handleChangeCardPack = () => {
  if (Object.values(editingCardPack.value).filter(Boolean).length !== 10) {
    return
  }
  cardPack.value = [...editingCardPack.value]
}

const quickCardPackInput = ref<string>("")

const isValidCards = (cards: number[]): boolean =>
  cards.length == 10 &&
  cards.every(card =>
    Number.isInteger(card) &&
    card >= 1 &&
    card <= 99
  )

const handleQucikChangeCardPack = () => {
  const cards = quickCardPackInput.value
    .split(';')
    .map(value => Number(value.trim()))

  if (!isValidCards(cards)) {
    return
  }
  
  editingCardPack.value = cards
}

const handleVote = (cardIndex: number) => {
  selectedCardIndex.value = cardIndex
  emit("vote", cardPack.value[cardIndex])
}

const handleChangeInputType = () => {
  emit("change-input-type", InputType.keyboard)
}
</script>
