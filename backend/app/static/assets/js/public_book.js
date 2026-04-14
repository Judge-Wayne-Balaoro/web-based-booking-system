// static/assets/js/public_book.js
import { ENDPOINTS } from "./config.js";
import { apiFetch } from "./api.js";

/**
 * Expects these elements in book.html:
 * - <input type="date" id="event_date">
 * - <p id="availability"></p>   (or any element with id="availability")
 * - <form id="bookingForm"> ... </form>
 */

const eventDateEl = document.getElementById("event_date");
const availabilityEl = document.getElementById("availability");
const bookingForm = document.getElementById("bookingForm");

// Prevent selecting past dates (uses user's local date)
if (eventDateEl) {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, "0");
  const dd = String(today.getDate()).padStart(2, "0");
  eventDateEl.min = `${yyyy}-${mm}-${dd}`;
}
// If you have a hidden input in the form, set its id to "event_date_hidden"
const eventDateHidden = document.getElementById("event_date_hidden");

// Helper: show text
function setAvailabilityText(text) {
  if (availabilityEl) availabilityEl.innerText = text;
}

// --------- AVAILABILITY CHECK ----------
window.checkAvailability = async function () {
  const date = eventDateEl?.value;

  if (!date) {
    setAvailabilityText("⚠️ Please pick a date first.");
    return;
  }

  try {
    // Your API returns: { success: true, data: { event_date, available } }
    const res = await apiFetch(
      `${ENDPOINTS.availability}?event_date=${encodeURIComponent(date)}`
    );

    console.log("Availability API response:", res);

    const available = res?.data?.available === true;

    if (available) {
      setAvailabilityText("✅ Date Available");
      // If you have hidden input, keep it synced
      if (eventDateHidden) eventDateHidden.value = date;
    } else {
      setAvailabilityText("❌ Date Already Reserved");
      if (eventDateHidden) eventDateHidden.value = "";
    }
  } catch (err) {
    setAvailabilityText(`❌ Availability check failed: ${err.message}`);
  }
};

// --------- CREATE BOOKING (WITH RECEIPT) ----------
if (bookingForm) {
  bookingForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const date = eventDateEl?.value;
    if (!date) {
      alert("Pick an event date first.");
      return;
    }

    try {
      const form = new FormData(bookingForm);

      // Make sure event_date is included (if your backend expects it)
      // If your form already has <input name="event_date">, this will overwrite/add.
      form.set("event_date", date);

      const raw = await fetch(ENDPOINTS.createBooking, {
        method: "POST",
        body: form, // multipart/form-data (do not set Content-Type manually)
      });

      const res = await raw.json();
      console.log("Create booking response:", res);

      if (!raw.ok) {
        alert(res?.detail || "Booking failed.");
        return;
      }

      // Common pattern in your API: { success: true, data: {...} }
      const bookingCode =
        res?.data?.booking_code ||
        res?.data?.code ||
        res?.booking_code ||
        res?.code ||
        null;

      alert(    
        bookingCode
          ? `✅ Booking created!\nBooking Code: ${bookingCode}\nStatus: PENDING`
          : `✅ Booking created!\nResponse: ${JSON.stringify(res)}`
      );

      bookingForm.reset();
      setAvailabilityText("");
      if (eventDateHidden) eventDateHidden.value = "";
      // keep date if you want:
      // eventDateEl.value = date;

    } catch (err) {
      alert("Booking error: " + err.message);
    }
  });
}