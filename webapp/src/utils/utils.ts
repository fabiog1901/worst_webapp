import axios from "axios";
import type { Job, Degree } from "@/types";

export const nextElementInList = <T>(arr: T[], val: T): T => {
  const idx = arr.indexOf(val);
  const nextIdx = (idx + 1) % arr.length;
  return arr[nextIdx];
};

export const getJobs = async (): Promise<Job[]> => {
  const r = await axios.get<Job[]>(`${import.meta.env.VITE_APP_API_URL}/jobs`);
  return r.data;
};

export const getDegrees = async (): Promise<Degree[]> => {
  const r = await axios.get<Degree[]>(
    `${import.meta.env.VITE_APP_API_URL}/degrees`
  );
  return r.data;
};
