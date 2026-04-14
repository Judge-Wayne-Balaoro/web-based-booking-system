document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('admin_token');
    
    // SECURITY CHECK: If there is no token, kick them back to the login page!
    if (!token) {
        window.location.href = '/admin/login.html';
        return;
    }

    const tableBody = document.getElementById('bookingsTableBody');
    const resultDiv = document.getElementById('dashboardResult');
    const logoutBtn = document.getElementById('logoutBtn');
    
    // Modal elements
    const receiptModal = document.getElementById('receiptModal');
    const receiptImage = document.getElementById('receiptImage');
    const closeModalBtn = document.getElementById('closeModalBtn');

    // Fetch the bookings when the page loads
    fetchBookings();

    async function fetchBookings() {
        try {
            // Notice the headers! We have to send the Authorization Bearer token
            const response = await fetch('/api/admin/bookings', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                // Token is invalid or expired
                localStorage.removeItem('admin_token');
                window.location.href = '/admin/login.html';
                return;
            }

            const data = await response.json();
            
            if (data.success) {
                renderTable(data.data.items);
            } else {
                showResult('Failed to load bookings.', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showResult('Network error while loading bookings.', 'error');
        }
    }

    function renderTable(bookings) {
        tableBody.innerHTML = ''; // Clear existing rows

        if (bookings.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No bookings found.</td></tr>';
            return;
        }

        bookings.forEach(booking => {
            const row = document.createElement('tr');
            
            // Format the status with colors
            let statusColor = 'black';
            if (booking.status === 'PENDING') statusColor = '#f39c12';
            if (booking.status === 'RESERVED') statusColor = '#27ae60';
            if (booking.status === 'REJECTED' || booking.status === 'CANCELLED') statusColor = '#e74c3c';

            // Create the HTML for the row
            row.innerHTML = `
                <td><strong>${booking.booking_code}</strong></td>
                <td>${booking.guest_name}</td>
                <td>${booking.event_date}</td>
                <td>${booking.pax}</td>
                <td>₱${booking.deposit_amount}</td>
                <td style="color: ${statusColor}; font-weight: bold;">${booking.status}</td>
                <td>
                    ${booking.status === 'PENDING' ? `
                        <button class="action-btn btn-approve" onclick="updateStatus(${booking.id}, 'approve')">Approve</button>
                        <button class="action-btn btn-reject" onclick="updateStatus(${booking.id}, 'reject')">Reject</button>
                    ` : ''}
                    </td>
            `;
            tableBody.appendChild(row);
        });
    }

    // This function handles the Approve and Reject buttons
    window.updateStatus = async function(bookingId, action) {
        if (!confirm(`Are you sure you want to ${action} this booking?`)) return;

        try {
            const response = await fetch(`/api/admin/bookings/${bookingId}/${action}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                showResult(`Booking successfully ${action}d!`, 'success');
                fetchBookings(); // Refresh the table
            } else {
                showResult(`Failed to ${action} booking: ${data.message}`, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showResult('Network error.', 'error');
        }
    };

    // Logout Functionality
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('admin_token');
        window.location.href = '/admin/login.html';
    });

    // Close Modal Functionality
    closeModalBtn.addEventListener('click', () => {
        receiptModal.style.display = 'none';
    });

    function showResult(message, type) {
        resultDiv.textContent = message;
        resultDiv.className = `result-message ${type}`;
        resultDiv.classList.remove('hidden');
        
        // Hide success messages after 3 seconds
        if(type === 'success'){
            setTimeout(() => resultDiv.classList.add('hidden'), 3000);
        }
    }
});