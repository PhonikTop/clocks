<template>
    <div class="total__block">
        <label>Общая оценка:</label>
        <div>
        <span></span> ч.
        </div>
        <button id="again">Еще раз</button>
    </div>
</template>
<style>
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

#again {
  margin-top: 10px;
  font-size: 1rem;
  color: #fff;
  background: #7F67F1;
  padding: 5px 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
</style>
