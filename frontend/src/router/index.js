import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Login",
    component: () => import("@/views/LoginPage.vue"),
  },
  {
    path: "/room/:room_id(\\d+)",
    name: "Room",
    component: () => import("@/views/RoomPage.vue"),
    props: true,
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/",
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
