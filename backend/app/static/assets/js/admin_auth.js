import { ENDPOINTS } from "./config.js";

document.getElementById("loginForm").addEventListener("submit", async function(e){

    e.preventDefault();

    const form = new FormData(this);

    const data = {
        username: form.get("username"),
        password: form.get("password")
    };

    const res = await fetch(ENDPOINTS.adminLogin,{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify(data)
    });

    const result = await res.json();

    localStorage.setItem("token", result.access_token);

    window.location.href="dashboard.html";

});