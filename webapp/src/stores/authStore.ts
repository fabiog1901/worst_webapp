import { defineStore } from "pinia";
import { useRouter } from "vue-router";
import { ref } from "vue";

import axios from "axios";

export const useAuthStore = defineStore("auth", () => {
  const router = useRouter();
  const user = ref(JSON.parse(localStorage.getItem("user") as string));
  const returnUrl = ref("/");

  const login = async (username: string, password: string) => {
    const token = await axios
      .post(
        `${import.meta.env.VITE_APP_API_URL}/login`,
        {
          username: username,
          password: password,
        },
        {
          headers: { "content-type": "application/x-www-form-urlencoded" },
        }
      )
      .then((r: any) => {
        return r.data;
      })
      .catch((error: any) => {
        console.error(error.response);
        logout();
      });

    if (token) {
      console.info(`authStore::login (${username})`);
      // update pinia state
      user.value = token;

      // store user details and jwt in local storage to keep user logged in between page refreshes
      localStorage.setItem("user", JSON.stringify(user));
      // redirect to previous url or default to home page
      router.push(returnUrl.value || "/");
    }
  };

  const logout = () => {
    user.value = null;
    localStorage.removeItem("user");
    router.push("/login");
    console.info("authStore::logout");
  };

  return {
    login,
    logout,
    user,
    returnUrl,
  };
});
