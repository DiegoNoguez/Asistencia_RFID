document.getElementById("loginForm").addEventListener("submit", function(e) {
  e.preventDefault();

  const rol = document.getElementById("rol").value;  // rol: 1, 2, 3
  const matricula = document.getElementById("matricula").value;
  const password = document.getElementById("password").value;

  const loginData = {
    usuario: matricula,
    password: password,
    rol: parseInt(rol)
  };

  fetch("http://localhost:8000/login/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(loginData)
  })
  .then(async (response) => {
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Error desconocido");
    }
    return response.json();
  })
  .then(data => {
    console.log("Respuesta del servidor:", data); // <-- Este console.log DEBE mostrar el JSON completo

    if (data.message === "Login exitoso") {
      localStorage.setItem("usuario", JSON.stringify(data)); // Guardar usuario

      // Redirigir
      if (data.rol === 1) window.location.href = "/static/alumno.html";
      else if (data.rol === 2) window.location.href = "/static/profesor.html";
      else if (data.rol === 3) window.location.href = "/static/admin_panel.html";
    } else {
      document.getElementById("error").textContent = "Credenciales incorrectas.";
    }
  })
  .catch(error => {
    console.error("Error al hacer login:", error);
    document.getElementById("error").textContent = "Hubo un error al hacer login: " + error.message;
  });
});


