// glossary-tooltips.js — no plural/irregular logic (one key only)

function slugify(s){
  return (s || "")
    .toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/&/g, "and")
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .trim();
}

async function fetchFirstOk(urls){
  for (const u of urls){
    try {
      const r = await fetch(u, { cache: "no-cache" });
      if (r.ok) return await r.json();
    } catch (_) {}
  }
  throw new Error("No glossary.json found at any candidate URL");
}

document.addEventListener("DOMContentLoaded", async () => {
  // Build a few robust candidates for where glossary.json might live
  const parts = location.pathname.split("/").filter(Boolean);
  const guesses = [
    // relative to current page
    new URL("glossary.json", document.baseURI).href,
    // repo subdir (e.g., /your-repo/ on GitHub Pages)
    parts.length ? `/${parts[0]}/glossary.json` : "/glossary.json",
    // absolute root fallback
    "/glossary.json",
  ];

  let glossary;
  try {
    glossary = await fetchFirstOk(guesses);
  } catch (err) {
    console.error("🔥 Failed to load glossary.json:", err);
    return;
  }

  document.querySelectorAll(".glossary-link").forEach(link => {
    const href = link.getAttribute("href") || "";
    // Prefer the explicit slug from href (#glossary-<slug>) if present
    const m = href.match(/#glossary-([^#?]+)/);
    const slugFromHref = m ? m[1] : null;

    const raw = link.dataset.term || link.textContent || "";
    const fallbackSlug = slugify(raw);

    const key = slugFromHref || fallbackSlug;
    const def = glossary[key];

    if (!def) return;

    // Init tooltip (requires Tippy.js on the page)
    if (typeof tippy === "function"){
      tippy(link, {
        content: `<strong>${raw}</strong><br>${def}`,
        allowHTML: true,
        theme: "light-border",
        placement: "top",
        delay: [100, 100],
        maxWidth: 300,
      });
    }
  });
});
