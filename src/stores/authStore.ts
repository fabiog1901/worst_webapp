import { defineStore } from "pinia";
import { useRouter } from "vue-router";
import { ref } from "vue";

import axios from "axios";
// import { axiosWrapper } from "@/utils/utils";

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

  const get_auth_code_url = async () => {
    const token = await axios
      .get(`${import.meta.env.VITE_APP_API_URL}/authorization_code`)
      .then((r: any) => {
        if (r.data) {
          (window.open(r.data, "_self") as Window).focus();
        }
      })
      .catch((error: any) => {
        console.error(error.response);
        logout();
      });
    console.log("token ==> ", token);
  };

  const get_token = async (auth_code: string) => {
    const token = await axios
      .get(`${import.meta.env.VITE_APP_API_URL}/token`, {
        params: { authorization_code: auth_code },
        headers: { "content-type": "application/x-www-form-urlencoded" },
      })
      .then((r: any) => {
        return r.data;
      })
      .catch((error: any) => {
        console.error(error.response);
        logout();
      });

    if (token) {
      console.info(`authStore::login `, token);
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
    get_auth_code_url,
    get_token,
    login,
    logout,
    user,
    returnUrl,
  };
});
