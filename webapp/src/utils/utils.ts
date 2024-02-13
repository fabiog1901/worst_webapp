import axios from "axios";
import { useAuthStore } from "@/stores/authStore";
import { useDateFormat } from "@vueuse/core";

import exportFromJSON from "export-from-json";

export const nextElementInList = <T>(arr: T[], val: T): T => {
  const idx = arr.indexOf(val);
  const nextIdx = (idx + 1) % arr.length;
  return arr[nextIdx];
};

export const formatDecimal = (value: any) => {
  if (value) {
    return value.toLocaleString(undefined, {
      maximumFractionDigits: 2,
      minimumFractionDigits: 2,
    });
  }

  return "";
};

export const formatDate = (value: any) => {
  if (value) {
    return useDateFormat(value, "YYYY-MM-DD").value;
  }
  return "";
};

export const formatDateTime = (value: any) => {
  if (value) {
    return useDateFormat(value, "YYYY-MM-DD HH:mm").value;
  }
  return "";
};

export const hashCode = (s: string) => {
  let hash = 0,
    i,
    chr;
  if (!s || s.length === 0) {
    return hash;
  }
  for (i = 0; i < s.length; i++) {
    chr = s.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return Math.abs(hash);
};

export const getLabel = (s: string) => {
  switch (hashCode(s) % 9) {
    case 0:
      return "bg-indigo-500";
    case 1:
      return "bg-purple-600";
    case 2:
      return "bg-teal-400";
    case 3:
      return "bg-orange-400";
    case 4:
      return "bg-rose-600";
    case 5:
      return "bg-amber-400";
    case 6:
      return "bg-lime-600";
    case 7:
      return "bg-emerald-600";
    case 8:
      return "bg-fuchsia-400";
  }
};

export const titleCase = (s: string) =>
  s
    .replace(/^[-_]*(.)/, (_, c) => c.toUpperCase()) // Initial char (after -/_)
    .replace(/[-_]+(.)/g, (_, c) => "_" + c.toUpperCase()); // First char after each -/_

const authStore = useAuthStore();

axios.defaults.baseURL = import.meta.env.VITE_APP_API_URL;
axios.defaults.headers.post["Content-Type"] = "application/json";

// export const sendFile = async (presigned_url: string, payload: any) => {
//   await axios.put(presigned_url, payload, {
//     headers: {
//       "Content-Type": "text/plain",
//     },
//   });
// };

export const save_to_csv = (data: any, id: string) => {
  if (!data) return;
  try {
    // returns "20240202_135807"
    const ts = new Date()
      .toISOString()
      .substring(0, 19)
      .replace(/[\W_]+/g, "")
      .replace("T", "_");
    const fileName = `worst.${id}.${ts}`;
    const exportType = exportFromJSON.types.csv;
    exportFromJSON({ data, fileName, exportType });
  } catch (e) {
    throw new Error("Parsing failed!");
  }
};

export const axiosWrapper = {
  get: request("GET"),
  post: request("POST"),
  put: request("PUT"),
  patch: request("PATCH"),
  delete: request("DELETE"),
};

function request(method: string) {
  return (url: string, body: any = {}, params: any = {}) => {
    const config: any = {
      method: method,
      url: url,
      data: body,
      params: params,
      //data: new URLSearchParams(body),
      headers: {
        Authorization: `Bearer ${authStore.user.access_token}`,
      },
    };

    return axios(config)
      .then((r) => {
        return r.data;
      })
      .catch((error) => {
        if (error.response.status === 401) {
          console.error("not authorized");
          authStore.logout();
        } else {
          // TODO handle 422 gracefully
          //return error.response;
          authStore.logout();
        }
      });
  };
}
