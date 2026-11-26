const navigation = document.querySelector("#primary-nav");
const navigationToggle = document.querySelector("#nav-toggle");
const navigationLinks = [...document.querySelectorAll(".primary-nav a")];
const sections = navigationLinks
  .map((link) => document.querySelector(link.getAttribute("href")))
  .filter(Boolean);

if (navigation && navigationToggle) {
  navigationToggle.addEventListener("click", () => {
    const isOpen = navigation.classList.toggle("is-open");
    navigationToggle.setAttribute("aria-expanded", String(isOpen));
    navigationToggle.setAttribute(
      "aria-label",
      isOpen ? "Close navigation" : "Open navigation",
    );
  });

  navigationLinks.forEach((link) => {
    link.addEventListener("click", () => {
      navigation.classList.remove("is-open");
      navigationToggle.setAttribute("aria-expanded", "false");
      navigationToggle.setAttribute("aria-label", "Open navigation");
    });
  });
}

if ("IntersectionObserver" in window && sections.length) {
  const sectionObserver = new IntersectionObserver(
    (entries) => {
      const visibleSections = entries
        .filter((entry) => entry.isIntersecting)
        .sort((left, right) => right.intersectionRatio - left.intersectionRatio);
      if (!visibleSections.length) return;

      const currentId = `#${visibleSections[0].target.id}`;
      navigationLinks.forEach((link) => {
        if (link.getAttribute("href") === currentId) {
          link.classList.add("active");
          link.setAttribute("aria-current", "location");
        } else {
          link.classList.remove("active");
          link.removeAttribute("aria-current");
        }
      });
    },
    { rootMargin: "-18% 0px -65% 0px", threshold: [0, 0.1, 0.5] },
  );

  sections.forEach((section) => sectionObserver.observe(section));
}

const checkForm = document.querySelector("#url-check-form");
const urlInput = document.querySelector("#url-input");
const characterCount = document.querySelector("#character-count");
const checkButton = document.querySelector("#check-button");
const resultCard = document.querySelector("#url-result");
const resultSymbol = document.querySelector("#result-symbol");
const resultMessage = document.querySelector("#result-message");
const resultDetail = document.querySelector("#result-detail");
const inputValidation = document.querySelector("#input-validation");
const MAX_URL_LENGTH = 4096;

function updateCharacterCount() {
  if (!urlInput || !characterCount) return;
  characterCount.textContent = `${urlInput.value.length.toLocaleString()} / ${MAX_URL_LENGTH.toLocaleString()}`;
}

function showResult(result) {
  if (!resultCard || !resultMessage || !resultDetail || !resultSymbol) return;
  const kind = ["success", "warning", "error"].includes(result.kind)
    ? result.kind
    : "error";
  resultCard.className = `result-card result-${kind}`;
  resultSymbol.textContent = kind === "success" ? "✓" : kind === "warning" ? "?" : "!";
  resultMessage.textContent = result.message || "The lookup could not be completed.";
  resultDetail.textContent = result.detail || "";
  resultCard.hidden = false;
}

function showValidation(message) {
  if (!inputValidation) return;
  inputValidation.textContent = message;
  inputValidation.hidden = false;
  urlInput?.setAttribute("aria-invalid", "true");
}

function clearValidation() {
  if (!inputValidation) return;
  inputValidation.textContent = "";
  inputValidation.hidden = true;
  urlInput?.removeAttribute("aria-invalid");
}

urlInput?.addEventListener("input", () => {
  updateCharacterCount();
  clearValidation();
});
updateCharacterCount();

checkForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearValidation();

  const url = urlInput.value.trim();
  if (!url) {
    showValidation("Enter a URL or text value to check.");
    urlInput.focus();
    return;
  }
  if (url.length > MAX_URL_LENGTH) {
    showValidation(`Input must be ${MAX_URL_LENGTH.toLocaleString()} characters or fewer.`);
    urlInput.focus();
    return;
  }

  urlInput.value = url;
  checkButton.disabled = true;
  checkButton.classList.add("is-loading");
  checkButton.setAttribute("aria-busy", "true");
  checkForm.setAttribute("aria-busy", "true");

  try {
    const response = await fetch(checkForm.action, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json",
      },
      body: new URLSearchParams(new FormData(checkForm)),
    });
    const result = await response.json();
    showResult(result);
  } catch (_error) {
    showResult({
      kind: "error",
      message: "The lookup could not be completed.",
      detail: "The local dashboard did not return a valid response. Please try again.",
    });
  } finally {
    checkButton.disabled = false;
    checkButton.classList.remove("is-loading");
    checkButton.removeAttribute("aria-busy");
    checkForm.removeAttribute("aria-busy");
  }
});
