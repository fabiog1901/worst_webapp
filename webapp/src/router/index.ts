import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "@/stores/authStore";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: () => import("@/layout/AppLayout.vue"),
      children: [
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
          component: () => import("@/views/TableView.vue"),
        },
        {
          path: "/:model/:id",
          component: () => import("@/views/InstanceView.vue"),
        },
        {
          path: "/:model/:id/:child_model_name",
          component: () => import("@/views/TableChildView.vue"),
        },
      ],
    },
    {
      path: "/login",
      component: () => import("@/views/LoginView.vue"),
    },
    {
      path: "/callback",
      component: () => import("@/views/CallbackView.vue"),
    },
  ],
  scrollBehavior() {
    return { top: 0, left: 0, behavior: "smooth" };
  },
});

export default router;

router.beforeEach(async (to) => {
  const authStore = useAuthStore();
  // redirect to login page if not logged in and trying to access a restricted page
  if (
    // make sure the user is authenticated
    !authStore.user &&
    // Avoid an infinite redirect
    to.path !== "/login" &&
    to.path !== "/callback"
  ) {
    // save where user wanted to go
    authStore.returnUrl = to.fullPath;

    console.warn(
      "Not authorized or not logged in. Redirecting...",
      to.fullPath
    );
    return "/login";
  }
});
