document.addEventListener("DOMContentLoaded", async () => {
  console.log("DOM ready");

  try {
    const res = await fetch("/scripts/glossary.json", {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }});
    console.log("Fetch status:", res.status);

    const glossary = await res.json();

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