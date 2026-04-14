import { ENDPOINTS } from "./config.js";
import { apiFetch } from "./api.js";

window.track = async function(){

    const code = document.getElementById("booking_code").value;

    const data = await apiFetch(`${ENDPOINTS.trackBooking}/${code}`);

    document.getElementById("status").innerText =
        "Status: " + data.status;
};