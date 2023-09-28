import { createRouter, createWebHashHistory } from "vue-router";

import { useAuthStore } from "@/stores/authStore";

const router = createRouter({
  history: createWebHashHistory(),
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
          component: () => import("@/views/ModelView.vue"),
        },
        {
          path: "/:model/:id",
          component: () => import("@/views/ModelDetailsView.vue"),
        },
      ],
    },
    {
      path: "/login",
      component: () => import("@/views/LoginView.vue"),
    },
  ],
  scrollBehavior() {
    return { top: 0, left: 0, behavior: "smooth" };
  },
});

export default router;

router.beforeEach(async (to) => {
  // redirect to login page if not logged in and trying to access a restricted page
  const authStore = useAuthStore();
  console.warn(authStore.user, to.path, to.path !== "/login", !authStore.user);

  if (
    // make sure the user is authenticated
    !authStore.user &&
    // Avoid an infinite redirect
    to.path !== "/login"
  ) {
    // save where user wanted to go
    authStore.returnUrl = to.fullPath;

    console.error("Not authorized or not logged in. Redirecting...");
    return "/login";
  }
});
