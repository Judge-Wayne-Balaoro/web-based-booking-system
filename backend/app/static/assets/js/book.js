// --- THE "BLACKED OUT" DATES (Update this manually for now) ---
// Format must be YYYY-MM-DD
const takenDates = [
    "2026-03-15", 
    "2026-03-22", 
    "2026-04-04"
];

// --- AVAILABILITY CHECKER LOGIC ---
document.getElementById('checkAvailabilityBtn').addEventListener('click', function() {
    const dateInput = document.getElementById('event_date').value;
    const resultDiv = document.getElementById('availabilityResult');
    const msg = document.getElementById('availabilityMessage');
    const proceedBtn = document.getElementById('proceedToBookBtn');

    if (!dateInput) {
        alert("Please select a date first!");
        return;
    }

    // 1. Show "Checking" state
    msg.innerHTML = `<span class="text-slate-400 italic">Consulting the Palacio calendar...</span>`;
    resultDiv.classList.remove('hidden');
    proceedBtn.classList.add('hidden'); // Hide proceed initially

    setTimeout(() => {
        // 2. Check if the selected date is in our "Taken" list
        if (takenDates.includes(dateInput)) {
            msg.innerHTML = `<span class="text-red-500 font-bold">🚫 Sorry, this date is fully booked.</span>`;
            proceedBtn.classList.add('hidden');
        } else {
            msg.innerHTML = `<span class="text-emerald-600 font-bold">✨ Great news! This date is available.</span>`;
            proceedBtn.classList.remove('hidden');
        }
    }, 1200);
});

// --- BOOKING FORM LOGIC ---
document.getElementById('bookingForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const btn = document.getElementById('submitBookingBtn');
    btn.innerText = "Securing your spot...";
    btn.disabled = true;

    setTimeout(() => {
        const randomID = Math.random().toString(36).substr(2, 6).toUpperCase();
        const bookingCode = `PF-2026-${randomID}`;

        document.getElementById('bookingForm').classList.add('hidden');
        const resultDiv = document.getElementById('bookingResult');
        resultDiv.classList.remove('hidden');
        
        document.getElementById('displayBookingCode').innerText = bookingCode;
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 2000); 
});