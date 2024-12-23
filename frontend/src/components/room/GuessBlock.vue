<template>
    <div class="guess__block">
        <label for="guess">Ваша оценка:</label>
        <div class="guess">
            <input id="guess" type="text"> ч.
        </div>
        <button id="make_guess">ОК</button>
    </div>
</template>
<style>
.guess__block label {
  font-size: 1rem;
  display: block;
  margin-bottom: 5px;
}
.guess {
  display: inline-block;
  position: relative;
}

#guess {
  width: 80px;
  padding: 5px;
  font-size: 1rem;
  text-align: center;
  border: 1px solid #ccc;
  border-radius: 4px;
  outline: none;
}

.guess__block button {
  font-size: 1rem;
  color: #fff;
  background: #7F67F1;
  padding: 5px 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
}
</style>
