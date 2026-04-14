import { ENDPOINTS } from "./config.js";
import { apiFetch } from "./api.js";

const tbody = document.getElementById("tbody");
const msg = document.getElementById("msg");
const statusFilter = document.getElementById("statusFilter");
const btnRefresh = document.getElementById("btnRefresh");
const btnLogout = document.getElementById("btnLogout");

function getToken() {
  return localStorage.getItem("token");
}

function requireAuthOrRedirect() {
  const token = getToken();
  if (!token) {
    window.location.href = "../admin/login.html";
    return null;
  }
  return token;
}

function setMsg(text, ok = true) {
  msg.textContent = text;
  msg.style.color = ok ? "green" : "red";
}

function pick(obj, keys, fallback = "") {
  for (const k of keys) {
    if (obj && obj[k] !== undefined && obj[k] !== null) return obj[k];
  }
  return fallback;
}

async function loadBookings() {
  const token = requireAuthOrRedirect();
  if (!token) return;

  setMsg("Loading...", true);
  tbody.innerHTML = "";

  try {
    // GET /api/admin/bookings
    const data = await apiFetch(ENDPOINTS.adminBookings, {
      headers: { Authorization: `Bearer ${token}` }
    });

    // Handle common shapes:
    const items = Array.isArray(data) ? data : (data.items || data.bookings || []);

    const filter = statusFilter.value.trim();
    const filtered = filter ? items.filter(b => b.status === filter) : items;

    if (!filtered.length) {
      tbody.innerHTML = `<tr><td colspan="8">No bookings found.</td></tr>`;
      setMsg("Loaded. (0 results)", true);
      return;
    }

    for (const b of filtered) {
      const id = pick(b, ["id", "booking_id"]);
      const event_date = pick(b, ["event_date"]);
      const code = pick(b, ["booking_code", "code"]);
      const status = pick(b, ["status"]);
      const full_name = pick(b, ["full_name", "name"]);
      const contact = pick(b, ["contact_number", "contact", "phone"]);
      const receipt_url = pick(b, ["receipt_url", "receipt_path", "receipt"]);

      const receiptCell = receipt_url
        ? `<a href="${receipt_url}" target="_blank">View</a>`
        : `—`;

      const actions = `
        <button data-act="approve" data-id="${id}">Approve</button>
        <button data-act="reject" data-id="${id}">Reject</button>
        <button data-act="cancel" data-id="${id}">Cancel</button>
      `;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${id ?? ""}</td>
        <td>${event_date ?? ""}</td>
        <td>${code ?? ""}</td>
        <td>${status ?? ""}</td>
        <td>${full_name ?? ""}</td>
        <td>${contact ?? ""}</td>
        <td>${receiptCell}</td>
        <td>${actions}</td>
      `;
      tbody.appendChild(tr);
    }

    setMsg(`Loaded. (${filtered.length} results)`, true);

  } catch (err) {
    setMsg(`Failed to load bookings: ${err.message}`, false);
  }
}

async function doAction(action, bookingId) {
  const token = requireAuthOrRedirect();
  if (!token) return;

  try {
    // POST /api/admin/bookings/{id}/approve|reject|cancel
    await apiFetch(`${ENDPOINTS.adminBookings}/${bookingId}/${action}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }
    });

    setMsg(`Success: ${action.toUpperCase()}`, true);
    await loadBookings();
  } catch (err) {
    setMsg(`Action failed: ${err.message}`, false);
  }
}

tbody.addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;

  const action = btn.dataset.act;
  const id = btn.dataset.id;
  if (!action || !id) return;

  doAction(action, id);
});

btnRefresh.addEventListener("click", loadBookings);
statusFilter.addEventListener("change", loadBookings);

btnLogout.addEventListener("click", () => {
  localStorage.removeItem("token");
  window.location.href = "../admin/login.html";
});

// initial load
loadBookings();