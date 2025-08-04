document.addEventListener("DOMContentLoaded", () => {
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

    if (userTitle) {
      const segments = userTitle.split(/(\$[^$]+\$)/); // math parts like $...$

      const renderPromises = segments.map(segment => {
        if (segment.startsWith("$") && segment.endsWith("$")) {
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
        // Add icon title
        const labelSpan = document.createElement("span");
        labelSpan.className = "callout-label";
        labelSpan.textContent = defaultLabel;
        titleDiv.appendChild(labelSpan);
        titleDiv.appendChild(document.createTextNode("⠀")); // spacer after label


        nodes.forEach((n, i) => {
          const prev = nodes[i - 1];
          const next = nodes[i + 1];
          const isMath = n.tagName?.toLowerCase().startsWith("mjx");

          // Add spacing before and/or after math if adjacent to text
          if (isMath) {
            if (prev && prev.nodeType === Node.ELEMENT_NODE && !prev.tagName?.startsWith("MJX")) {
              titleDiv.appendChild(document.createTextNode("\u00A0")); // space before math
            }

            titleDiv.appendChild(n);

            if (next && next.nodeType === Node.ELEMENT_NODE && !next.tagName?.startsWith("MJX")) {
              titleDiv.appendChild(document.createTextNode("\u00A0")); // space after math
            }
          } else {
            titleDiv.appendChild(n);
          }
        });

        div.insertBefore(titleDiv, div.firstChild);

        if (isCollapsible) {
          div.setAttribute("data-collapse", "true");
          titleDiv.addEventListener("click", () => {
            div.classList.toggle("callout-open");
          });
        }
      }).catch(err => {
        console.error("MathJax render error:", err);
        titleDiv.textContent = `${defaultLabel} ⠀ ${userTitle}`;
        div.insertBefore(titleDiv, div.firstChild);
      });

    } else {
      // No title provided — just use icon
      titleDiv.textContent = defaultLabel;
      div.insertBefore(titleDiv, div.firstChild);

      if (isCollapsible) {
        div.setAttribute("data-collapse", "true");
        titleDiv.addEventListener("click", () => {
          div.classList.toggle("callout-open");
        });
      }
    }
  }

  document.querySelectorAll("div").forEach(processCalloutDiv);
});

