<template>
    <div class="observers__wrapper">
        <h3>Наблюдатели</h3>
        <div class="observers"></div>
    </div>
</template>
<script>
export default {
  data () {
    return {
      participants: {
        'd3b2d2e0-f7c5-4a4e-828c-67b2a5a8f4c3': { nickname: 'User1', role: 'voter' },
        '9a6d1a34-b0fc-4c8d-b5ed-11d8902ae547': { nickname: 'User2', role: 'voter' },
        '1b6e5d34-5c7e-45a8-92c3-c9dc9f5505d7': { nickname: 'User3', role: 'voter' },
        '774d7d3a-d1fc-496d-8049-21a1cd5612b1': { nickname: 'User4', role: 'voter' },
        '8a5c7139-34e4-4654-a6c1-b21d1f65b8b2': { nickname: 'User5', role: 'voter' },
        'c4ed4c96-1e06-4c23-b40c-a278db5105c4': { nickname: 'User6', role: 'observer' },
        '2eeec1b6-084a-45bb-add3-3bf1536cbf40': { nickname: 'User7', role: 'observer' }
      }
    }
  },
  computed: {
    observers () {
      return Object.values(this.participants).filter(participant => participant.role === 'observer')
    }
  }
}
</script>
<style>
.observers__wrapper {
  position: fixed;
  top: 0;
  right: 20px;
  text-align: right;
}

.observers h3 {
  font-size: 1.2rem;
  color: #6B6B6B;
}

.observers {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style>
