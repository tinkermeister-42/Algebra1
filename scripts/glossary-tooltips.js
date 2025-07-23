console.log("Running glossary tooltip loader...");

document.addEventListener("DOMContentLoaded", async () => {
  console.log("DOM ready");

  try {
    const res = await fetch("/glossary.json");
    console.log("Fetch status:", res.status);

    const glossary = await res.json();
    console.log("Glossary loaded:", glossary);

    document.querySelectorAll(".glossary-link").forEach(link => {
      const term = link.dataset.term?.toLowerCase();
      const def = glossary[term];
      if (def) {
        tippy(link, {
          content: `<strong>${term}</strong><br>${def}`,
          allowHTML: true,
          theme: 'light-border',
          placement: 'top',
          delay: [100, 100],
          maxWidth: 300,
        });
      }
    });
  } catch (err) {
    console.error("Tooltip loading failed:", err);
  }
});