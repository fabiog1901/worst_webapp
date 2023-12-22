import axios from "axios";
import { useAuthStore } from "@/stores/authStore";

export const nextElementInList = <T>(arr: T[], val: T): T => {
  const idx = arr.indexOf(val);
  const nextIdx = (idx + 1) % arr.length;
  return arr[nextIdx];
};

const { user, logout } = useAuthStore();

axios.defaults.baseURL = import.meta.env.VITE_APP_API_URL;
axios.defaults.headers.common["Authorization"] = `Bearer ${user.access_token}`;
axios.defaults.headers.post["Content-Type"] = "application/json";

export const axiosWrapper = {
  get: request("GET"),
  post: request("POST"),
  put: request("PUT"),
  delete: request("DELETE"),
};

function request(method: string) {
  return (url: string, body: any = {}) => {
    const config: any = {
      method: method,
      url: url,
      data: body,
      //data: new URLSearchParams(body),
    };

    return axios(config)
      .then((r) => {
        return r.data;
      })
      .catch((error) => {
        console.error(error.response);
        logout();
      });
  };
}
