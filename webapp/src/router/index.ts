import { createRouter, createWebHashHistory } from "vue-router";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: "/",
      component: () => import("@/views/HomeView.vue"),
    },
    {
      path: "/admin",
      component: () => import("@/views/AdminView.vue"),
    },
    {
      path: "/:model",
      component: () => import("@/views/ModelView.vue"),
    },
    {
      path: "/:model/:id",
      component: () => import("@/views/ModelDetailsView.vue"),
    },
  ],
  scrollBehavior() {
    return { top: 0, left: 0, behavior: "smooth" };
  },
});

export default router;
