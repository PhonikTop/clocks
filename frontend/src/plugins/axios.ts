import axios from "axios";

const csrfToken = document.cookie
  .split("; ")
  .find((row) => row.startsWith("csrftoken="))
  ?.split("=")[1];

const api = axios.create({
  baseURL: "/api/v1",
  timeout: 20000,
  headers: {
    "X-CSRFToken": csrfToken,
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: unknown) => {
    if (error instanceof Error) return Promise.reject(error);
    return Promise.reject(new Error(String(error)));
  }
);

export default api;
