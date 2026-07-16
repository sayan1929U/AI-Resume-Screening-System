// --- Auth handling ---
const authPanel = document.getElementById("auth-panel");
const protectedContent = document.getElementById("protected-content");
const appContent = document.getElementById("app-content");
const authError = document.getElementById("auth-error");
const authStatus = document.getElementById("auth-status");
const userEmailEl = document.getElementById("user-email");

const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const showSignupLink = document.getElementById("show-signup");
const logoutBtn = document.getElementById("logout-btn");

function getToken() {
  return localStorage.getItem("ats_token");
}

function setToken(token, email) {
  localStorage.setItem("ats_token", token);
  if (email) localStorage.setItem("ats_email", email);
}

function clearToken() {
  localStorage.removeItem("ats_token");
  localStorage.removeItem("ats_email");
}

function showLoggedIn() {
  authPanel.hidden = true;
  protectedContent.hidden = false;
  appContent.hidden = false;
  userEmailEl.textContent = localStorage.getItem("ats_email") || "";
}

function showLoggedOut(message) {
  clearToken();
  authPanel.hidden = false;
  protectedContent.hidden = true;
  appContent.hidden = true;
  if (message) authStatus.textContent = message;
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

if (getToken()) {
  showLoggedIn();
} else {
  showLoggedOut();
}

showSignupLink.addEventListener("click", (e) => {
  e.preventDefault();
  loginForm.hidden = !loginForm.hidden;
  signupForm.hidden = !signupForm.hidden;
  authError.textContent = "";
});

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  authError.textContent = "";
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  try {
    const body = new URLSearchParams();
    body.append("username", email);
    body.append("password", password);

    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Login failed.");
    }

    const data = await res.json();
    setToken(data.access_token, email);
    showLoggedIn();
  } catch (err) {
    authError.textContent = err.message;
  }
});

signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  authError.textContent = "";
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;

  try {
    const res = await fetch("/api/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, role: "recruiter" }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Signup failed.");
    }

    const data = await res.json();
    setToken(data.access_token, email);
    showLoggedIn();
  } catch (err) {
    authError.textContent = err.message;
  }
});

logoutBtn.addEventListener("click", () => {
  showLoggedOut("Signed out. Sign in to continue.");
});

// --- Upload / ranking ---
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const fileListEl = document.getElementById("file-list");
const submitBtn = document.getElementById("submit-btn");
const statusLine = document.getElementById("status-line");
const uploadForm = document.getElementById("upload-form");

const resultsPanel = document.getElementById("results-panel");
const resultsBody = document.getElementById("results-body");
const resultsCount = document.getElementById("results-count");
const errorSummary = document.getElementById("error-summary");
const footerIndex = document.getElementById("footer-index");

let selectedFiles = [];

function renderFileList() {
  fileListEl.innerHTML = "";
  selectedFiles.forEach((file, idx) => {
    const li = document.createElement("li");
    const sizeKb = (file.size / 1024).toFixed(0);
    li.innerHTML = `<span>${file.name} &middot; ${sizeKb} KB</span><span class="remove-file" data-idx="${idx}">✕</span>`;
    fileListEl.appendChild(li);
  });
  submitBtn.disabled = selectedFiles.length === 0;
}

function addFiles(fileArray) {
  for (const f of fileArray) {
    if (!selectedFiles.some(existing => existing.name === f.name && existing.size === f.size)) {
      selectedFiles.push(f);
    }
  }
  renderFileList();
}

dropzone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (e) => {
  addFiles(Array.from(e.target.files));
  fileInput.value = "";
});

["dragenter", "dragover"].forEach(evt => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
  });
});

["dragleave", "drop"].forEach(evt => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
  });
});

dropzone.addEventListener("drop", (e) => {
  addFiles(Array.from(e.dataTransfer.files));
});

fileListEl.addEventListener("click", (e) => {
  if (e.target.classList.contains("remove-file")) {
    const idx = Number(e.target.dataset.idx);
    selectedFiles.splice(idx, 1);
    renderFileList();
  }
});

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (selectedFiles.length === 0) return;

  submitBtn.disabled = true;
  statusLine.textContent = `Analyzing ${selectedFiles.length} resume(s)...`;
  resultsPanel.hidden = true;
  errorSummary.hidden = true;

  const formData = new FormData();
  selectedFiles.forEach(f => formData.append("files", f));

  try {
    const res = await fetch("/api/recruiter/upload", {
      method: "POST",
      headers: authHeaders(),
      body: formData,
    });

    if (res.status === 401) {
      showLoggedOut("Session expired. Please sign in again.");
      return;
    }

    if (!res.ok) {
      throw new Error(`Server responded with ${res.status}`);
    }

    const data = await res.json();
    renderResults(data);
    statusLine.textContent = "Done.";
  } catch (err) {
    statusLine.textContent = `Failed: ${err.message}`;
  } finally {
    submitBtn.disabled = selectedFiles.length === 0;
  }
});

function renderResults(data) {
  resultsBody.innerHTML = "";
  const candidates = data.candidates || [];

  candidates.forEach((c) => {
    const scorePct = Math.round(c.overall_score ?? 0);
    const skillsTags = (c.matching_skills || [])
      .slice(0, 4)
      .map(s => `<span class="skill-tag">${s}</span>`)
      .join("");

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${c.rank}</td>
      <td>
        <div class="candidate-name">${c.filename}</div>
        <div class="candidate-skills">${skillsTags}</div>
      </td>
      <td>
        <span class="score-value">${scorePct}</span>
        <div class="score-bar-track"><div class="score-bar-fill" style="width:${scorePct}%"></div></div>
      </td>
      <td><span class="recommendation-tag rec-${(c.recommendation || "").toLowerCase().replace(/\s+/g, "-")}">${c.recommendation || ""}</span></td>
    `;
    resultsBody.appendChild(tr);
  });

  resultsCount.textContent = `${data.total_candidates ?? candidates.length} candidates`;
  footerIndex.textContent = `${candidates.length} / ${data.total_candidates ?? candidates.length}`;

  if (data.failed && data.failed > 0) {
    errorSummary.hidden = false;
    const errorLines = (data.errors || [])
      .map(e => `${e.filename}: ${e.error}`)
      .join(" | ");
    errorSummary.textContent = `${data.failed} file(s) failed — ${errorLines}`;
  }

  resultsPanel.hidden = false;
}

// --- History ---
const loadHistoryBtn = document.getElementById("load-history-btn");
const historyTable = document.getElementById("history-table");
const historyBody = document.getElementById("history-body");
const historyStatus = document.getElementById("history-status");

loadHistoryBtn.addEventListener("click", async () => {
  historyStatus.textContent = "Loading...";
  try {
    const res = await fetch("/api/recruiter/history", {
      headers: authHeaders(),
    });

    if (res.status === 401) {
      showLoggedOut("Session expired. Please sign in again.");
      return;
    }

    if (!res.ok) throw new Error(`Server responded with ${res.status}`);

    const data = await res.json();
    historyBody.innerHTML = "";

    data.history.forEach((h) => {
      const uploadedDate = new Date(h.uploaded_at).toLocaleString();
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${h.filename}</td>
        <td>${uploadedDate}</td>
        <td>${Math.round(h.overall_score)}</td>
        <td>${h.recommendation || ""}</td>
      `;
      historyBody.appendChild(tr);
    });

    historyTable.hidden = false;
    historyStatus.textContent = `${data.total} past result(s) loaded.`;
  } catch (err) {
    historyStatus.textContent = `Failed to load history: ${err.message}`;
  }
});