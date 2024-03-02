import { defineStore } from "pinia";
import { useRouter } from "vue-router";
import { ref } from "vue";

import axios from "axios";

export const useAuthStore = defineStore("auth", () => {
  const router = useRouter();
  const id_token = ref(JSON.parse(localStorage.getItem("id_token") as string));
  const access_token = ref(
    JSON.parse(localStorage.getItem("access_token") as string),
  );
  const fullname = ref("");
  const returnUrl = ref("/");

  const get_auth_config = () => {
    return axios
      .get(`${import.meta.env.VITE_APP_API_URL}/auth_config`)
      .then((r: any) => {
        return r.data;
      })
      .catch((error: any) => {
        console.error(error.response);
        logout();
      });
  };

  const logout = () => {
    id_token.value = null;
    localStorage.removeItem("user");
    router.push("/login");
    console.info("authStore::logout");
  };

  return {
    get_auth_config,
    logout,
    id_token,
    access_token,
    fullname,
    returnUrl,
  };
});
