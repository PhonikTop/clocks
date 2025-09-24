import { defineStore } from "pinia"

export const useTimerStore = defineStore("timer", {
  state: () => ({
    timeEndTS: null as null | number, 
    timeLeft: null as null | number,
  }),
  getters: {
    formattedTime: (state) => {
      if (state.timeLeft === null) return null;
      const totalSeconds = Math.floor(state.timeLeft / 1000);
      const minutes = Math.floor((totalSeconds % 3600) / 60)
        .toString()
        .padStart(2, '0');
      const seconds = (totalSeconds % 60).toString().padStart(2, '0');
      return `${minutes}:${seconds}`;
    },
  },

  actions: {
    updateTime(endTimestamp: number) {
      if (endTimestamp === null) return;
      this.timeEndTS = endTimestamp
      const now = Date.now();
      this.timeLeft = Math.max(endTimestamp - now, 0);
      if (this.timeLeft === 0) this.resetTimer();
    },
    resetTimer() {
      if (this.timeEndTS === null) return;
      this.timeEndTS = null;
      this.timeLeft = null;
    }
  },
})
