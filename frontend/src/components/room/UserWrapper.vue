<template>
    <div class="users__wrapper">
    <div class="users">
        <div class="user">
        <div v-for="participant in voters" :key="participant" class="user__name">
            <p>{{ participant.nickname }}</p>
            <span v-if="votes[participant]" class="mark"></span>
        </div>
        </div>
    </div>
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
      },
      votes: {
        'd3b2d2e0-f7c5-4a4e-828c-67b2a5a8f4c3': { vote: 10, nickname: 'User1' },
        '9a6d1a34-b0fc-4c8d-b5ed-11d8902ae547': { vote: 5, nickname: 'User2' },
        '8a5c7139-34e4-4654-a6c1-b21d1f65b8b2': { vote: 7, nickname: 'User5' }
      }
    }
  },
  computed: {
    voters () {
      return Object.values(this.participants).filter(participant => participant.role === 'voter')
    }
  }
}
</script>
<style>
.users {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.user {
  padding: 10px;
  background: #F8F8F8;
  border-radius: 8px;
  display: inline-block;
  text-align: center;
}

.user__name p {
  margin: 0;
  font-size: 1rem;
}

.user__name .mark {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #7F67F1;
  border-radius: 50%;
}
</style>
