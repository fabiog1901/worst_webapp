import { defineStore } from "pinia";
import axios from "axios";
import { useRouter } from "vue-router";
import { ref } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const router = useRouter();
  const user = ref(JSON.parse(localStorage.getItem("user") as string));
  const returnUrl = ref("/");

  const login = async (username: string, password: string) => {
    const r = await axios.post<{}>(
      `${import.meta.env.VITE_APP_API_URL}/login`,
      {
        username: username,
        password: password,
      },
      {
        headers: { "content-type": "application/x-www-form-urlencoded" },
      }
    );

    console.info("modelStore: fetched all worst_models");

    // update pinia state
    user.value = r.data;

    // store user details and jwt in local storage to keep user logged in between page refreshes
    localStorage.setItem("user", JSON.stringify(user));
    console.log(
      `YO: ${user.value.access_token} - ${JSON.stringify(user.value)}`
    );
    console.log(`YO2: ${returnUrl.value}`);

    // redirect to previous url or default to home page
    router.push(returnUrl.value || "/");
  };

  const logout = () => {
    user.value = null;
    localStorage.removeItem("user");
    router.push("/login");
  };

  return {
    login,
    logout,
    user,
    returnUrl,
  };
});
