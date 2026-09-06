const API_BASE = import.meta.env.VITE_API_URL || "";

export async function request(path, options = {}) {
  const headers = {
    ...(options.body
      ? { "Content-Type": "application/json" }
      : {}),
    ...(options.headers || {}),
  };

  const token = localStorage.getItem("staywise_token");

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  const text = await response.text();

  let data = null;

  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = {
      detail: text,
    };
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      data?.error ||
      `Request failed (${response.status})`
    );
  }

  return data;
}

export const api = {
  // ---------------------------------------------------------
  // System
  // ---------------------------------------------------------

  health: () =>
    request("/api/healthz"),

  // ---------------------------------------------------------
  // Authentication
  // ---------------------------------------------------------

  me: () =>
    request("/api/auth/me"),

  login: (data) =>
    request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  register: (data) =>
    request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // ---------------------------------------------------------
  // Hotels
  // ---------------------------------------------------------

  hotels: (params = {}) =>
    request(
      `/api/hotels?${new URLSearchParams(
        Object.entries(params).filter(
          ([, value]) =>
            value !== "" &&
            value !== undefined &&
            value !== null
        )
      )}`
    ),

  hotel: (id) =>
    request(`/api/hotels/${id}`),

  // ---------------------------------------------------------
  // Guest bookings
  // ---------------------------------------------------------

  bookings: () =>
    request("/api/bookings"),

  createBooking: (data) =>
    request("/api/bookings", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // ---------------------------------------------------------
  // Razorpay payment
  // ---------------------------------------------------------

  createOrder: (id) =>
    request(`/api/bookings/${id}/create-order`, {
      method: "POST",
    }),

  verifyPayment: (id, data) =>
    request(`/api/bookings/${id}/verify-payment`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // ---------------------------------------------------------
  // Cancellation
  // ---------------------------------------------------------

  cancel: (id) =>
    request(`/api/bookings/${id}/cancel`, {
      method: "POST",
    }),

  // ---------------------------------------------------------
  // Refund policy
  // ---------------------------------------------------------

  refundPolicy: () =>
    request("/api/refund-policy"),

  // ---------------------------------------------------------
  // Owner dashboard
  // ---------------------------------------------------------

  ownerDashboard: () =>
    request("/api/owner/dashboard"),

  ownerBookings: () =>
    request("/api/owner/bookings"),

  updateBooking: (id, status) =>
    request(
      `/api/owner/bookings/${id}/status`,
      {
        method: "PUT",
        body: JSON.stringify({
          status,
        }),
      }
    ),

  // ---------------------------------------------------------
  // Owner hotels
  // ---------------------------------------------------------

  createHotel: (data) =>
    request("/api/owner/hotels", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateHotel: (id, data) =>
    request(`/api/owner/hotels/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  createRoom: (hotelId, data) =>
    request(
      `/api/owner/hotels/${hotelId}/rooms`,
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    ),
};