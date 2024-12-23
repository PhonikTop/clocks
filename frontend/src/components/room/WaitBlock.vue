<template>
    <div class="wait__block">
        <div class="user__start">
        <img src="http://teamtaskestimator.com/assets/images/clock.svg" alt="">
        <p>Ожидаем...</p>
        </div>
    </div>
</template>
<style>
.wait__block .user__start {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.wait__block img {
  width: 32px;
  height: 32px;
}

.wait__block p {
  font-size: 1rem;
  color: #6B6B6B;
}

</style>
