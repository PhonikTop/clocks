import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/JoinView.vue'
import RoomView from '../views/RoomView.vue'

const routes = [
  {
    path: '/',
    name: 'user-join',
    component: HomeView
  },
  {
    path: '/room',
    name: 'room',
    component: RoomView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
