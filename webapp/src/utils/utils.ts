import axios from "axios";
import type { Account, Opportunity, Contact } from "@/types";

export const nextElementInList = <T>(arr: T[], val: T): T => {
  const idx = arr.indexOf(val);
  const nextIdx = (idx + 1) % arr.length;
  return arr[nextIdx];
};

export const getAccounts = async (): Promise<Account[]> => {
  const r = await axios.get<Account[]>(
    `${import.meta.env.VITE_APP_API_URL}/accounts`
  );
  return r.data;
};

export const getOpportunities = async (): Promise<Opportunity[]> => {
  const r = await axios.get<Opportunity[]>(
    `${import.meta.env.VITE_APP_API_URL}/opportunities`
  );
  return r.data;
};

export const getContacts = async (): Promise<Contact[]> => {
  const r = await axios.get<Contact[]>(
    `${import.meta.env.VITE_APP_API_URL}/contactswithaccountname`
  );
  return r.data;
};
