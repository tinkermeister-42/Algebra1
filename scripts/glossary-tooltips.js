


document.addEventListener("DOMContentLoaded", async () => {
  console.log("DOM ready");
    
    // Get base path ("/Algebra1/" on GitHub Pages, "/" locally)
    const pathParts = window.location.pathname.split("/");
    const isLocal = location.hostname === "localhost";
    const basePath = isLocal ? "/" : `/${pathParts[1]}/`;
    
    fetch(`${basePath}glossary.json`)
      .then(res => res.json())
      .then(glossary => {
        console.log("✅ Glossary loaded:", glossary);
        // Tooltip logic here
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
      })
      .catch(err => {
        console.error("🔥 Failed to load glossary.json:", err);
      });
});