<template>
  <div class="users__wrapper">
    <div class="users">
      <div v-for="participant in voters" :key="participant.nickname" class="user__name">
        <p>{{ participant.nickname }}</p>
        <span v-if="votes[participant.id]" class="mark"></span>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    participants: {
      type: Object,
      required: true
    },
    votes: {
      type: Object,
      required: true
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
  margin: auto;
  width: 600px;
  max-width: 80%;
  background: #F8F8F8;
  border-radius: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  text-align: center;
  justify-content: center;
}

.user__name p {
  margin: 10px;
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
