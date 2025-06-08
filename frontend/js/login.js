document.addEventListener("DOMContentLoaded", () => {
  const rolSelect = document.getElementById("rol");
  rolSelect.addEventListener("change", () => {
    const mat = document.getElementById("matricula");
    mat.placeholder = rolSelect.value === "profesor" ? "Clave Profesor" : "Matrícula";
  });
});

document.getElementById("loginForm").addEventListener("submit", function(e) {
  e.preventDefault();
  const rol = document.getElementById("rol").value;
  const matricula = document.getElementById("matricula").value;
  const password = document.getElementById("password").value;

  const user = usuariosSimulados.find(u => u.rol === rol && u.matricula === matricula && u.password === password);

  if (user) {
    localStorage.setItem("usuario", JSON.stringify(user));
    if (rol === "profesor") window.location.href = "dashboard-profesor.html";
    else if (rol === "alumno") window.location.href = "alumno.html";
    else window.location.href = "admin_panel.html";
  } else {
    document.getElementById("error").textContent = "Credenciales incorrectas.";
  }
});
