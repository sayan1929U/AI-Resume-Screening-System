/* =========================================================================
   AI RESUME SCREENING SYSTEM — CLIENT SCRIPT
   Handles: theme persistence, navbar/scroll effects, ambient particles,
   mouse-following glow, scroll-reveal animations, animated counters,
   the live demo pipeline (real upload + AI status sequence), FAQ
   accordion, and PDF export.
   ========================================================================= */

(function () {
  "use strict";

  /* -----------------------------------------------------------------------
     1. THEME (dark / light) — persisted in localStorage
     ----------------------------------------------------------------------- */
  const THEME_KEY = "ai-resume-theme";
  const root = document.documentElement;
  const themeToggle = document.getElementById("themeToggle");

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
  }

  const savedTheme = localStorage.getItem(THEME_KEY);
  if (savedTheme) {
    applyTheme(savedTheme);
  } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
    applyTheme("light");
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") || "dark";
      applyTheme(current === "dark" ? "light" : "dark");
    });
  }

  /* -----------------------------------------------------------------------
     2. NAVBAR — glass on scroll + mobile menu
     ----------------------------------------------------------------------- */
  const navbar = document.getElementById("navbar");
  const navToggle = document.getElementById("navToggle");
  const navbarNav = document.getElementById("navbarNav");

  function onScroll() {
    if (window.scrollY > 24) {
      navbar.classList.add("is-scrolled");
    } else {
      navbar.classList.remove("is-scrolled");
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (navToggle && navbarNav) {
    navToggle.addEventListener("click", () => {
      const isOpen = navbarNav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });

    navbarNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        navbarNav.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* -----------------------------------------------------------------------
     3. AMBIENT PARTICLES — generated once, floats via CSS
     ----------------------------------------------------------------------- */
  const particlesContainer = document.getElementById("particles");
  if (particlesContainer) {
    const PARTICLE_COUNT = 22;
    const accentColors = ["var(--indigo)", "var(--cyan)", "var(--violet)", "var(--electric-blue)"];

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const particle = document.createElement("span");
      particle.className = "particle";
      const left = Math.random() * 100;
      const duration = 14 + Math.random() * 14;
      const delay = Math.random() * -duration;
      const color = accentColors[i % accentColors.length];

      particle.style.left = left + "%";
      particle.style.top = 70 + Math.random() * 30 + "%";
      particle.style.animationDuration = duration + "s";
      particle.style.animationDelay = delay + "s";
      particle.style.background = color;
      particle.style.boxShadow = `0 0 14px 3px ${color}`;

      particlesContainer.appendChild(particle);
    }
  }

  /* -----------------------------------------------------------------------
     4. MOUSE-FOLLOWING GRADIENT GLOW
     ----------------------------------------------------------------------- */
  const cursorGlow = document.getElementById("cursorGlow");
  if (cursorGlow) {
    let ticking = false;
    window.addEventListener(
      "mousemove",
      (e) => {
        if (!ticking) {
          window.requestAnimationFrame(() => {
            const xPct = (e.clientX / window.innerWidth) * 100;
            const yPct = (e.clientY / window.innerHeight) * 100;
            cursorGlow.style.setProperty("--glow-x", xPct + "%");
            cursorGlow.style.setProperty("--glow-y", yPct + "%");
            ticking = false;
          });
          ticking = true;
        }
      },
      { passive: true }
    );
  }

  /* -----------------------------------------------------------------------
     5. SCROLL-REVEAL ANIMATIONS
     ----------------------------------------------------------------------- */
  const revealTargets = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealTargets.length) {
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry, i) => {
          if (entry.isIntersecting) {
            setTimeout(() => entry.target.classList.add("is-visible"), i * 60);
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -60px 0px" }
    );
    revealTargets.forEach((el) => revealObserver.observe(el));
  } else {
    revealTargets.forEach((el) => el.classList.add("is-visible"));
  }

  /* -----------------------------------------------------------------------
     6. HERO PROGRESS BARS — animate width in once visible
     ----------------------------------------------------------------------- */
  document.querySelectorAll(".progress__bar[data-fill]").forEach((bar) => {
    const target = bar.getAttribute("data-fill") + "%";
    const barObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            requestAnimationFrame(() => (bar.style.width = target));
            barObserver.unobserve(bar);
          }
        });
      },
      { threshold: 0.4 }
    );
    barObserver.observe(bar);
  });

  /* -----------------------------------------------------------------------
     7. ANIMATED COUNTERS
     ----------------------------------------------------------------------- */
  const counters = document.querySelectorAll(".counter");
  function animateCounter(el) {
    const target = parseFloat(el.getAttribute("data-target"));
    const duration = 1400;
    const start = performance.now();

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(target * eased);
      if (progress < 1) requestAnimationFrame(tick);
      else el.textContent = target;
    }
    requestAnimationFrame(tick);
  }

  if ("IntersectionObserver" in window && counters.length) {
    const counterObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            counterObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    counters.forEach((el) => counterObserver.observe(el));
  }

  /* -----------------------------------------------------------------------
     8. FAQ ACCORDION
     ----------------------------------------------------------------------- */
  document.querySelectorAll(".accordion__trigger").forEach((trigger) => {
    trigger.addEventListener("click", () => {
      const item = trigger.closest(".accordion__item");
      const panel = item.querySelector(".accordion__panel");
      const isOpen = trigger.getAttribute("aria-expanded") === "true";

      document.querySelectorAll(".accordion__trigger").forEach((t) => {
        if (t !== trigger) {
          t.setAttribute("aria-expanded", "false");
          t.closest(".accordion__item").querySelector(".accordion__panel").style.maxHeight = null;
        }
      });

      trigger.setAttribute("aria-expanded", String(!isOpen));
      panel.style.maxHeight = isOpen ? null : panel.scrollHeight + "px";
    });
  });

  /* -----------------------------------------------------------------------
     9. RESUME UPLOAD FIELD — click-to-browse + selected filename display
     ----------------------------------------------------------------------- */
  const resumeInput = document.getElementById("resumeFile");
  const uploadDrop = document.querySelector(".upload-drop");
  const uploadDropText = document.querySelector(".upload-drop__text");
  const uploadDropDefaultText = uploadDropText ? uploadDropText.textContent : "";

  if (uploadDrop && resumeInput && uploadDropText) {
    resumeInput.addEventListener("change", () => {
      const file = resumeInput.files[0];
      uploadDropText.textContent = file ? file.name : uploadDropDefaultText;
    });
  }

  /* -----------------------------------------------------------------------
     10. LIVE DEMO PIPELINE — real upload + AI status sequence
     ----------------------------------------------------------------------- */
  const demoForm = document.getElementById("demoForm");
  const demoLoading = document.getElementById("demoLoading");
  const resultDashboard = document.getElementById("resultDashboard");
  const loadingStatus = document.getElementById("loadingStatus");
  const loadingStepsList = document.getElementById("loadingSteps");
  const loadingSteps = loadingStepsList ? Array.from(loadingStepsList.children) : [];
  const resetDemoBtn = document.getElementById("resetDemoBtn");
  const analyzeBtn = document.getElementById("analyzeBtn");

  const UPLOAD_ENDPOINT = "/api/upload/upload";
  const STEP_DURATION_MS = 650;

  function initials(name) {
    if (!name) return "AI";
    const parts = name.trim().split(/\s+/);
    return (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
  }

  /** Steps the loading list through its states. Resolves once the full
   *  sequence has finished animating, independent of the network call. */
  function runLoadingSequence() {
    return new Promise((resolve) => {
      let step = 0;
      loadingSteps.forEach((li) => li.classList.remove("is-active", "is-done"));

      function next() {
        if (step > 0) {
          loadingSteps[step - 1].classList.remove("is-active");
          loadingSteps[step - 1].classList.add("is-done");
        }

        if (step < loadingSteps.length) {
          loadingSteps[step].classList.add("is-active");
          if (loadingStatus && loadingStatus.firstChild) {
            loadingStatus.firstChild.textContent =
              step < loadingSteps.length - 1 ? "AI Thinking" : "Wrapping up";
          }
          step++;
          setTimeout(next, STEP_DURATION_MS);
        } else {
          setTimeout(resolve, 400);
        }
      }
      next();
    });
  }

  /** Applies whatever the server (or the demo fallback) decided about the
   *  candidate to the result dashboard. */
  function renderResult(formValues, serverResult) {
    const data = serverResult || {};

    const name = data.candidate_name || formValues.name;
    const role = data.role || formValues.role;
    const experience = data.experience || formValues.experience;
    const education = data.education || formValues.education;
    const email = data.email || formValues.email;

    const atsScore = data.ats_score ?? 94;
    const jobMatch = data.job_match ?? 91;
    const skillMatch = data.skill_match ?? 92;
    const confidence = data.confidence ?? 88;
    const recommendation = data.recommendation || "Highly Recommended";
    const skills = Array.isArray(data.matching_skills) && data.matching_skills.length
      ? data.matching_skills
      : ["Python", "FastAPI", "Docker", "AWS", "TensorFlow"];

    document.getElementById("resultName").textContent = name;
    document.getElementById("resultRole").textContent = role;
    document.getElementById("resultExperience").textContent = experience;
    document.getElementById("resultEducation").textContent = education;
    document.getElementById("resultEmail").textContent = email;
    document.getElementById("resultInitials").textContent = initials(name);
    document.getElementById("resultRecommendation").textContent = recommendation;

    const scoreRings = resultDashboard.querySelectorAll(".score-ring");
    const scoreValues = [atsScore, jobMatch, skillMatch, confidence];
    scoreRings.forEach((ring, i) => {
      const value = scoreValues[i];
      if (value === undefined) return;
      ring.style.setProperty("--score", value);
      const num = ring.querySelector(".score-ring__num");
      if (num) num.textContent = value;
    });

    const techSkillsList = document.getElementById("resultTechSkills");
    if (techSkillsList) {
      techSkillsList.innerHTML = skills
        .map((skill) => `<li class="tag">${skill}</li>`)
        .join("");
    }
  }

  if (demoForm) {
    demoForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const file = resumeInput ? resumeInput.files[0] : null;
      if (!file) {
        alert("Please upload your resume first.");
        return;
      }

      const formValues = {
        name: document.getElementById("candidateName").value || "Priya Sharma",
        role: document.getElementById("role").value || "Senior ML Engineer",
        experience: document.getElementById("experience").value || "5 Years",
        education: document.getElementById("education").value || "B.Tech, Computer Science",
        email: demoForm.querySelector('[name="email"]').value || "candidate@example.com",
      };

      demoForm.hidden = true;
      demoLoading.hidden = false;
      resultDashboard.hidden = true;
      if (analyzeBtn) analyzeBtn.disabled = true;

      const uploadData = new FormData();
      uploadData.append("file", file);
      uploadData.append("candidate_name", formValues.name);
      uploadData.append("role", formValues.role);

      const uploadPromise = fetch(UPLOAD_ENDPOINT, {
        method: "POST",
        body: uploadData,
      }).then((response) => {
        if (!response.ok) {
          throw new Error("Upload failed with status " + response.status);
        }
        return response.json();
      });

      try {
        const [serverResult] = await Promise.all([uploadPromise, runLoadingSequence()]);
        renderResult(formValues, serverResult);
      } catch (err) {
        console.error(err);
        demoLoading.hidden = true;
        demoForm.hidden = false;
        if (analyzeBtn) analyzeBtn.disabled = false;
        alert("Resume analysis failed. Please try again.");
        return;
      }

      if (analyzeBtn) analyzeBtn.disabled = false;
      demoLoading.hidden = true;
      resultDashboard.hidden = false;
      resultDashboard.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  if (resetDemoBtn) {
    resetDemoBtn.addEventListener("click", () => {
      resultDashboard.hidden = true;
      demoForm.hidden = false;
      demoForm.reset();
      if (uploadDropText) uploadDropText.textContent = uploadDropDefaultText;
      demoForm.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  const compareBtn = document.getElementById("compareBtn");
  if (compareBtn) {
    compareBtn.addEventListener("click", () => {
      const label = compareBtn.querySelector("span");
      label.textContent = "Added to comparison";
      setTimeout(() => (label.textContent = "Compare Candidate"), 2200);
    });
  }

  /* -----------------------------------------------------------------------
     11. DOWNLOAD REPORT — client-side PDF export via jsPDF
     ----------------------------------------------------------------------- */
  const downloadBtn = document.getElementById("downloadReportBtn");
  if (downloadBtn) {
    downloadBtn.addEventListener("click", () => {
      if (!window.jspdf) {
        window.print();
        return;
      }

      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();

      const name = document.getElementById("resultName").textContent;
      const role = document.getElementById("resultRole").textContent;
      const email = document.getElementById("resultEmail").textContent;
      const experience = document.getElementById("resultExperience").textContent;
      const education = document.getElementById("resultEducation").textContent;
      const recommendation = document.getElementById("resultRecommendation").textContent;

      const scoreRings = resultDashboard.querySelectorAll(".score-ring__num");
      const [ats, jobMatch, skillMatch, confidence] = Array.from(scoreRings).map((el) => el.textContent);

      doc.setFont("helvetica", "bold");
      doc.setFontSize(18);
      doc.text("AI Resume Screening Report", 20, 24);

      doc.setFontSize(12);
      let y = 42;
      const line = (label, value) => {
        doc.setFont("helvetica", "bold");
        doc.text(label + ":", 20, y);
        doc.setFont("helvetica", "normal");
        doc.text(String(value), 70, y);
        y += 10;
      };

      line("Candidate", name);
      line("Role", role);
      line("Email", email);
      line("Experience", experience);
      line("Education", education);
      line("ATS Score", ats + "%");
      line("Job Match", jobMatch + "%");
      line("Skill Match", skillMatch + "%");
      line("Confidence", confidence + "%");
      line("Recommendation", recommendation);

      doc.save(`${name.replace(/\s+/g, "_")}_screening_report.pdf`);
    });
  }

  /* -----------------------------------------------------------------------
     12. WATCH DEMO — smooth-scrolls straight to the live demo section
     ----------------------------------------------------------------------- */
  const watchDemoBtn = document.getElementById("watchDemoBtn");
  if (watchDemoBtn) {
    watchDemoBtn.addEventListener("click", (e) => {
      e.preventDefault();
      document.getElementById("demo").scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
})();