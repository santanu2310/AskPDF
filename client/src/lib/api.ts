import axios from "axios";
import { BASE_URL } from "./endpoints";

export const request = axios.create({
  baseURL: BASE_URL,
});

export const authRequest = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
});
