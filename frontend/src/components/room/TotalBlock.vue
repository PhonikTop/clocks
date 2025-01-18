<template>
    <div class="total__block">
        <label>Общая оценка:</label>
        <div>
          <span></span> ч.
        </div>
        <div class="choise_buttons">
          <button class="choise_button">Перезапустить</button>
          <button class="choise_button">Далее</button>
          <button class="choise_button">Завершить</button>
        </div>
    </div>
</template>
<style scoped>
.total__block label {
  font-size: 1rem;
  margin-bottom: 5px;
  display: block;
}

.total__block div {
  font-size: 1.2rem;
  font-weight: bold;
  color: #6B6B6B;
}

.choise_buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: row;
  gap: 12px;
  margin-top: 14px;
}

.choise_button {
  font-family:system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  font-size: 17px;
  color: #fff;
  background: #7F67F1;
  padding: 5px 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
</style>
