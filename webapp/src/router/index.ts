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
      path: "/accounts",
      component: () => import("@/views/AccountsView.vue"),
    },
    {
      path: "/accounts/:account_id",
      component: () => import("@/views/AccountDetailsView.vue"),
    },
    {
      path: "/opportunities",
      component: () => import("@/views/OpportunitiesView.vue"),
    },
    {
      path: "/opportunities/:account_id/:opportunity_id",
      component: () => import("@/views/OpportunityDetailsView.vue"),
    },
    {
      path: "/artifacts",
      component: () => import("@/views/ArtifactsView.vue"),
    },
    {
      path: "/artifacts/:account_id/:opportunity_id/:artifact_id",
      component: () => import("@/views/ArtifactDetailsView.vue"),
    },
    {
      path: "/projects",
      component: () => import("@/views/ProjectsView.vue"),
    },
    {
      path: "/projects/:account_id/:opportunity_id/:project_id",
      component: () => import("@/views/ProjectDetailsView.vue"),
    },
    {
      path: "/contacts",
      component: () => import("@/views/ContactsView.vue"),
    },
    {
      path: "/contacts/:account_id/:contact_id",
      component: () => import("@/views/ContactDetailsView.vue"),
    },
    {
      path: "/tasks",
      component: () => import("@/views/TasksView.vue"),
    },
    {
      path: "/tasks/:account_id/:opportunity_id/:project_id/:task_id",
      component: () => import("@/views/TaskDetailsView.vue"),
    },
    {
      path: "/notes",
      component: () => import("@/views/NotesView.vue"),
    },
    {
      path: "/notes/:account_id/:note_id",
      component: () => import("@/views/NoteDetailsView.vue"),
    },
    {
      path: "/notes/:account_id/:opportunity_id/:note_id",
      component: () => import("@/views/NoteDetailsView.vue"),
    },
    {
      path: "/notes/:account_id/:opportunity_id/:project_id/:note_id",
      component: () => import("@/views/NoteDetailsView.vue"),
    },
  ],
  scrollBehavior() {
    return { top: 0, left: 0, behavior: "smooth" };
  },
});

export default router;
