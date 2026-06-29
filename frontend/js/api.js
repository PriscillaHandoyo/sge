/* ====================================================================
   SGE — API & Auth Helper
   Semua komunikasi ke backend FastAPI + handling JWT lewat sini.
   ==================================================================== */

const API_BASE = "http://localhost:8000";

/* ---------------- Token & JWT helpers ---------------- */

function getToken() {
  return sessionStorage.getItem("sge_token");
}

function setToken(token) {
  sessionStorage.setItem("sge_token", token);
}

function clearToken() {
  sessionStorage.removeItem("sge_token");
}

/**
 * Decode JWT payload TANPA verifikasi signature.
 * Ini cuma buat keperluan tampilan (nama user, role) di frontend.
 * Validasi asli (signature, expiry) tetap dilakukan backend tiap request.
 */
function decodeToken(token) {
  try {
    const payload = token.split(".")[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decoded);
  } catch (e) {
    return null;
  }
}

function getRole() {
  const token = getToken();
  if (!token) return null;
  const payload = decodeToken(token);
  return payload ? payload.role : null;
}

function getUsername() {
  const token = getToken();
  if (!token) return null;
  const payload = decodeToken(token);
  return payload ? payload.sub : null;
}

function isLoggedIn() {
  const token = getToken();
  if (!token) return false;
  const payload = decodeToken(token);
  if (!payload || !payload.exp) return false;
  return payload.exp * 1000 > Date.now();
}

/* ---------------- Path helper ---------------- */

/**
 * Hitung otomatis berapa "../" yang dibutuhin buat balik ke folder pages/ root,
 * berdasarkan seberapa dalam halaman saat ini (misal di pages/master/ = 1 level).
 * Ini bikin link ke dashboard.html / login.html selalu benar dari folder manapun.
 */
function getPagesRootPrefix() {
  const path = window.location.pathname;
  const marker = "/pages/";
  const idx = path.indexOf(marker);
  if (idx === -1) return "";

  const afterPages = path.slice(idx + marker.length);
  const depth = afterPages.split("/").length - 1; // jumlah subfolder di bawah pages/
  return "../".repeat(depth);
}

/* ---------------- Auth guard ---------------- */

/**
 * Panggil ini di awal tiap halaman SELAIN login.html.
 * Kalau belum login / token expired, otomatis lempar balik ke login.
 */
function requireAuth() {
  if (!isLoggedIn()) {
    clearToken();
    window.location.href = getPagesRootPrefix() + "login.html";
  }
}

function logout() {
  clearToken();
  window.location.href = getPagesRootPrefix() + "login.html";
}

/* ---------------- Fetch wrapper ---------------- */

/**
 * Bungkus fetch biasa, otomatis nempelin header Authorization
 * dan auto-redirect ke login kalau dapet 401 (token invalid/expired).
 */
async function apiFetch(path, options = {}) {
  const token = getToken();
  const isFormData = options.body instanceof FormData;

  const response = await fetch(API_BASE + path, {
    ...options,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (response.status === 401) {
    clearToken();
    window.location.href = getPagesRootPrefix() + "login.html";
    return null;
  }

  return response;
}
