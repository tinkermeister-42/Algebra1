function slugify(s){
  return s.toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/&/g, "and")
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .trim();
}
function singularizeLastWord(s){
  const w = s.toLowerCase().trim().split(/\s+/);
  if (!w.length) return s;
  let last = w[w.length - 1];
  if (last.endsWith("ies")) last = last.replace(/ies$/, "y");
  else if (/(s|x|z|ch|sh)es$/.test(last)) last = last.replace(/es$/, "");
  else if (last.endsWith("s") && !last.endsWith("ss")) last = last.replace(/s$/, "");
  w[w.length - 1] = last;
  return w.join(" ");
}
function pluralizeLastWord(s){
  const w = s.toLowerCase().trim().split(/\s+/);
  if (!w.length) return s;
  let last = w[w.length - 1];
  if (/[^aeiou]y$/.test(last)) last = last.replace(/y$/, "ies");
  else if (/(s|x|z|ch|sh)$/.test(last)) last = last + "es";
  else if (!/s$/.test(last)) last = last + "s";
  w[w.length - 1] = last;
  return w.join(" ");
}

document.addEventListener("DOMContentLoaded", () => {
  const pathParts = window.location.pathname.split("/");
  const isLocal = location.hostname === "localhost";
  const basePath = isLocal ? "/" : `/${pathParts[1]}/`;

  fetch(`${basePath}glossary.json?ts=${Date.now()}`, { cache: "no-cache" })
    .then(r => { if (!r.ok) throw new Error(`${r.status} ${r.statusText}`); return r.json(); })
    .then(glossary => {
      document.querySelectorAll(".glossary-link").forEach(link => {
        const href = link.getAttribute("href") || "";
        const m = href.match(/#glossary-([^#?]+)/);
        const slugFromHref = m ? m[1] : null;

        const raw = link.dataset.term || link.textContent || "";
        const candidates = [
          slugFromHref,
          slugify(raw),
          slugify(singularizeLastWord(raw)),
          slugify(pluralizeLastWord(raw))
        ].filter(Boolean);

        let def;
        for (const k of candidates) {
          if (glossary[k]) { def = glossary[k]; break; }
        }
        if (def) {
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
    })
    .catch(err => console.error("🔥 Failed to load glossary.json:", err));
});
