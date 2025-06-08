document.getElementById("loginForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  const rol = document.getElementById("rol").value;
  const matricula = document.getElementById("matricula").value;
  const password = document.getElementById("password").value;

  const loginData = {
    usuario: matricula,
    password: password,
    rol: parseInt(rol)
  };

  try {
    const response = await fetch("http://localhost:8000/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(loginData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Error en las credenciales");
    }

    const data = await response.json();
    console.log("Respuesta del servidor:", data);

    if (data.message === "Login exitoso") {
      localStorage.setItem("usuario", JSON.stringify(data));
      
      // Redirigir según rol
      switch(data.rol) {
        case 1: window.location.href = "alumno.html"; break;
        case 2: window.location.href = "dashboard-profesor.html"; break;
        case 3: window.location.href = "admin_panel.html"; break;
      }
    } else {
      document.getElementById("error").textContent = "Credenciales incorrectas.";
    }
  } catch (error) {
    console.error("Error al hacer login:", error);
    document.getElementById("error").textContent = error.message;
  }
});
