document.addEventListener("DOMContentLoaded", () => {
  const calloutTypes = [
    "answers", "answer", "objectives", "vocab", "real-world", "remember",
    "you-try", "you-try-m", "think", "gotcha"
  ];

  const iconMap = {
    answers: "✅ Answer Key",
    answer: "",              // no default label; use your title only
    objectives: "🎯 Objectives",
    vocab: "📚 Vocabulary",
    "real-world": "🌍 In the Real-World",
    remember: "📌 Remember",
    "you-try": "📝 You Try",
    "you-try-m": "📝 You Try",
    think: "💡 Think About It",
    gotcha: "⚠️ Caution!"
  };

  // Outer-collapsible callouts (answer intentionally NOT collapsible)
  const collapsible = new Set(["answer", "answers", "you-try", "think"]);

  function processCalloutDiv(div) {
    const match = calloutTypes.find(type => div.classList.contains(type));
    if (!match) return;

    const calloutType = match;
    div.classList.add(`callout-${calloutType}`, "callout");

    const isOuterCollapsible = collapsible.has(calloutType);
    const userTitle = div.getAttribute("title");
    const defaultLabel = iconMap[calloutType] ?? "ℹ️";

    const titleDiv = document.createElement("div");
    titleDiv.className = "callout-title";

    const insertTitle = (label, titleTextOrNodes) => {
      // Only add a label chip if non-empty
      if (label && label.trim().length > 0) {
        const labelSpan = document.createElement("span");
        labelSpan.className = "callout-label";
        labelSpan.textContent = label;
        titleDiv.appendChild(labelSpan);
        titleDiv.appendChild(document.createTextNode("⠀")); // spacer
      }

      if (Array.isArray(titleTextOrNodes)) {
        titleTextOrNodes.forEach(node => titleDiv.appendChild(node));
      } else {
        const span = document.createElement("span");
        span.className = "callout-title-sub";
        span.textContent = titleTextOrNodes ?? "";
        titleDiv.appendChild(span);
      }

      div.insertBefore(titleDiv, div.firstChild);

      if (isOuterCollapsible) {
        div.setAttribute("data-collapse", "true");
        titleDiv.addEventListener("click", () => {
          div.classList.toggle("callout-open");
        });
      }
    };

    if (userTitle) {
      const segments = userTitle.split(/(\$[^$]+\$)/); // inline math segments
      const renderPromises = segments.map(segment => {
        const isMath = segment.startsWith("$") && segment.endsWith("$");
        if (isMath && window.MathJax?.tex2chtmlPromise) {
          return MathJax.tex2chtmlPromise(segment, { display: false }).then(node => {
            node.classList.add("callout-title-sub");
            return node;
          });
        } else {
          const span = document.createElement("span");
          span.className = "callout-title-sub";
          span.textContent = segment;
          return Promise.resolve(span);
        }
      });

      Promise.all(renderPromises).then(nodes => {
        // add thin spacing around math nodes
        const spaced = [];
        nodes.forEach((n, i) => {
          const tag = n.tagName?.toLowerCase() || "";
          const prev = nodes[i - 1];
          const next = nodes[i + 1];
          const isMath = tag.startsWith("mjx");
          if (isMath && prev && !prev.tagName?.toLowerCase().startsWith("mjx")) {
            spaced.push(document.createTextNode("\u00A0"));
          }
          spaced.push(n);
          if (isMath && next && !next.tagName?.toLowerCase().startsWith("mjx")) {
            spaced.push(document.createTextNode("\u00A0"));
          }
        });
        insertTitle(defaultLabel, spaced);
      }).catch(() => {
        insertTitle(defaultLabel, userTitle);
      });
    } else {
      // No title; still insert a bar (with label only if present)
      insertTitle(defaultLabel, "");
    }

    // .you-try-m: no internal toggles; it stays open.
    // Place a separate .answer callout after it with your custom title.
  }

  document.querySelectorAll("div").forEach(processCalloutDiv);
});
