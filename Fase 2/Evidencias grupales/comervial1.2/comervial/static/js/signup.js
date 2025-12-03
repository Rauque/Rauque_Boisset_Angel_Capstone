(function () {
  const $ = (sel) => document.querySelector(sel);
  const username = $("#id_username");
  const email = $("#id_email");
  const p1 = $("#id_password1");
  const p2 = $("#id_password2");
  const ruleLen = $("#ruleLen");
  const ruleMix = $("#ruleMix");
  const pwMatchHint = $("#pwMatchHint");
  const submit = $("#btnSubmit");

  const reMix = /^(?=.*[A-Za-z])(?=.*\d).{8,16}$/;

  function checkPasswordRules() {
    const v = p1.value;
    // Largo
    const okLen = v.length >= 8 && v.length <= 16;
    ruleLen.classList.toggle("text-success", okLen);
    ruleLen.classList.toggle("text-danger", !okLen);

    // Mezcla
    const okMix = /[A-Za-z]/.test(v) && /\d/.test(v);
    ruleMix.classList.toggle("text-success", okMix);
    ruleMix.classList.toggle("text-danger", !okMix);

    // Valid / invalid on input
    p1.classList.toggle("is-valid", okLen && okMix);
    p1.classList.toggle("is-invalid", v.length > 0 && !(okLen && okMix));
    return okLen && okMix;
  }

  function checkPasswordsMatch() {
    const ok = p1.value.length > 0 && p1.value === p2.value;
    pwMatchHint.textContent = ok ? "Las contraseñas coinciden." : (p2.value ? "Las contraseñas no coinciden." : "");
    pwMatchHint.className = "form-text mt-1 " + (ok ? "text-success" : (p2.value ? "text-danger" : ""));
    p2.classList.toggle("is-valid", ok);
    p2.classList.toggle("is-invalid", p2.value.length > 0 && !ok);
    return ok;
  }

  // Debounce helper
  function debounce(fn, ms) {
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  }

  // Chequeo de disponibilidad de usuario
  const usernameHelp = $("#usernameHelp");
  const checkUsername = debounce(async () => {
    const u = (username.value || "").trim();
    username.classList.remove("is-valid", "is-invalid");
    usernameHelp.textContent = "";
    if (!u) return;
    try {
      const resp = await fetch(`/accounts/check-username/?username=${encodeURIComponent(u)}`);
      const data = await resp.json();
      if (data.taken) {
        username.classList.add("is-invalid");
        usernameHelp.textContent = "Este usuario ya existe.";
        usernameHelp.className = "form-text mt-1 text-danger";
      } else {
        username.classList.add("is-valid");
        usernameHelp.textContent = "Usuario disponible.";
        usernameHelp.className = "form-text mt-1 text-success";
      }
    } catch {
      // Silencio errores de red
    }
  }, 300);

  // Habilitar/Deshabilitar submit
  function updateSubmitState() {
    const okRules = checkPasswordRules();
    const okMatch = checkPasswordsMatch();
    const okUser = !username.classList.contains("is-invalid") && username.value.trim().length > 0;
    const okEmail = email.checkValidity(); // usa validación nativa del tipo email
    submit.disabled = !(okRules && okMatch && okUser && okEmail);
  }

  // Eventos
  p1.addEventListener("input", () => { checkPasswordRules(); checkPasswordsMatch(); updateSubmitState(); });
  p2.addEventListener("input", () => { checkPasswordsMatch(); updateSubmitState(); });
  username.addEventListener("input", () => { checkUsername(); updateSubmitState(); });
  email.addEventListener("input", updateSubmitState);

  // Estado inicial
  checkPasswordRules(); checkPasswordsMatch(); updateSubmitState();
})();
