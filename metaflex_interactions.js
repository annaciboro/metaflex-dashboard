// ============================================
// MetaFlex Dashboard - Interactions v1.0
// ============================================

document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ MetaFlex Interactions JS Loaded");

  // Fade nav shadow on scroll
  const nav = document.querySelector(
    "[data-testid='stVerticalBlock'] > [data-testid='stHorizontalBlock']:first-child"
  );
  if (nav) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 20) {
        nav.style.boxShadow = "0 4px 16px rgba(0, 0, 0, 0.08)";
      } else {
        nav.style.boxShadow = "none";
      }
    });
  }

  // Highlight active navigation button
  const buttons = document.querySelectorAll(
    "[data-testid='stVerticalBlock'] > [data-testid='stHorizontalBlock']:first-child button"
  );
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });
});
