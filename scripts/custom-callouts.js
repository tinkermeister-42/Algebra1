document.addEventListener("DOMContentLoaded", () => {
  // NO MathJax configuration here. Rely entirely on Quarto's MathJax load.

  const calloutTypes = [
    "answers", "objectives", "vocab", "real-world", "remember",
    "you-try", "think", "gotcha"
  ];

  const iconMap = {
    answers: "✅ Answer Key",
    objectives: "🎯 Objectives",
    vocab: "📚 Vocabulary",
    "real-world": "🌍 In the Real-World",
    remember: "📌 Remember",
    "you-try": "📝 You Try",
    think: "💡 Think About It",
    gotcha: "⚠️ Caution!"
  };

  const collapsible = new Set(["answers", "you-try", "think"]);

  // Function to process a single div for callout and math
  function processCalloutDiv(div) {
    const match = calloutTypes.find(type => div.classList.contains(type));
    if (!match) return;

    const calloutType = match;
    div.classList.add(`callout-${calloutType}`, "callout");

    const isCollapsible = collapsible.has(calloutType);
    const userTitle = div.getAttribute("title");
    const defaultLabel = iconMap[calloutType];

    const titleDiv = document.createElement("div");
    titleDiv.className = "callout-title";

    // Build the initial titleDiv content
    let titleContentHtml = defaultLabel;

    if (userTitle) {
      // Check if userTitle contains probable LaTeX commands (e.g., \frac, \sum, \times, etc.)
      // This regex looks for common LaTeX commands that indicate math.
      // You might need to adjust this regex based on the specific LaTeX you expect.
      const isMath = /\\(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|omicron|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|cdot|times|div|frac|sum|int|sqrt|left|right|begin|end|label|ref|text|mbox|textrm)/.test(userTitle) ||
                     /\{.*\}/.test(userTitle); // Also check for curly braces often used in math

      if (isMath) {
        // If it's likely math, create a placeholder span to be replaced by MathJax
        titleContentHtml += `&nbsp;&nbsp;&nbsp;&nbsp;<span class="math-source"><span class="callout-title-sub">${userTitle}</span></span>`;
        // Put the initial HTML into the titleDiv
        titleDiv.innerHTML = titleContentHtml;
        div.insertBefore(titleDiv, div.firstChild);

        const mathSourceSpan = titleDiv.querySelector(".math-source");

        // Now, process only if it contains MathJax content
        if (mathSourceSpan) {
            const mathContent = mathSourceSpan.textContent; // Get the raw LaTeX string

            if (window.MathJax && MathJax.tex2chtmlPromise) {
              MathJax.tex2chtmlPromise(mathContent, { display: false })
                .then((node) => {
                  mathSourceSpan.parentNode.replaceChild(node, mathSourceSpan);
                  console.log("MathJax tex2chtmlPromise completed for:", mathContent);
                })
                .catch(err => {
                  console.warn("MathJax tex2chtmlPromise rendering error for:", mathContent, err);
                });
            } else {
              // Fallback for when MathJax isn't immediately ready
              console.log("MathJax or tex2chtmlPromise not ready. Scheduling delayed typesetting for:", mathContent);
              const interval = setInterval(() => {
                if (window.MathJax && MathJax.tex2chtmlPromise) {
                  clearInterval(interval);
                  MathJax.tex2chtmlPromise(mathContent, { display: false })
                    .then((node) => {
                      mathSourceSpan.parentNode.replaceChild(node, mathSourceSpan);
                      console.log("MathJax tex2chtmlPromise completed (delayed) for:", mathContent);
                    })
                    .catch(err => {
                      console.warn("MathJax tex2chtmlPromise rendering error (delayed) for:", mathContent, err);
                    });
                }
              }, 50); // Check every 50ms
            }
        }
      } else {
        // If it's not math, just append the userTitle as plain text
        titleContentHtml += `󠀠󠁜󠁜&nbsp;&nbsp;&nbsp;&nbsp;<span class="callout-title-sub">${userTitle}</span>`;
        titleDiv.innerHTML = titleContentHtml;
        div.insertBefore(titleDiv, div.firstChild);
      }
    } else {
      // If no userTitle, just use the defaultLabel
      titleDiv.innerHTML = defaultLabel;
      div.insertBefore(titleDiv, div.firstChild);
    }

    if (isCollapsible) {
      div.setAttribute("data-collapse", "true");
      titleDiv.addEventListener("click", () => {
        div.classList.toggle("callout-open");
      });
    }
  }

  // Iterate over all relevant divs and process them
  document.querySelectorAll("div").forEach(processCalloutDiv);
});