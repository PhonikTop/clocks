<template>
    <div class="start-var">
        <form class="user-form">
            <select name="room_select">
            <option v-for="room in rooms" :key="room"> {{ room }} </option>
            </select>
            <input id="name" name="nickname" placeholder="Введите имя" type="text" />
            <div class="obs">
            <input type="checkbox" name="is_observer" id="observer" />
            <label for="observer"> Наблюдатель</label>
            </div>
            <button id="enter">Далее</button>
        </form>
    </div>
</template>
<script>
export default {
  data () {
    return {
      rooms: ['Деньги', 'Улучшение', 'ЫВОФВ', 'Chasiki']
    }
  }
}
</script>
<style>
.start-var {
  padding: 15px;
  border: 2.6px solid rgb(21,23,25);
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.5);
  width: 300px;
  height: 200px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 30px;
}
.user-form {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 15px;
  width: 100%;
  max-width: 300px;
  margin: 20px;
}

.user-form select,
.user-form input {
  padding: 8px;
  font-size: 16px;
  border: 2px solid var(--primary-color);
  border-radius: var(--border-radius);
}

.user-form button {
  padding: 10px;
  background-color: var(--primary-color);
  color: var(--secondary-color);
  font-size: 18px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: background-color 0.3s;
}

.user-form button:hover {
  background-color: #333;
  color:azure;
}

.observer {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
