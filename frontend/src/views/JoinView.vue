<template>
  <div class="content">
    <div class="wrapper">
      <JoinForm></JoinForm>
    </div>
  </div>
</template>
<script>
import JoinForm from '@/components/join/JoinForm.vue'

export default {
  name: 'HomeView',
  components: {
    JoinForm
  }
}
</script>
<style scoped>
@import '@/assets/styles/app.css';

.wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  width: 100%;
  height: 100%;
  gap: 30px;
}
</style>
