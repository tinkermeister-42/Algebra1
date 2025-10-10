function slugify(s){
  return s.toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/&/g, "and")
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .trim();
}

// --- Irregulars (last-word only) ---
const IRREGULAR_S2P = {
  axis: "axes",
  analysis: "analyses",
  basis: "bases",
  parenthesis: "parentheses",
  thesis: "theses",
  crisis: "crises",
  diagnosis: "diagnoses",
  hypothesis: "hypotheses",
  synthesis: "syntheses",
  synopsis: "synopses",
  ellipsis: "ellipses",
  oasis: "oases",
};
const IRREGULAR_P2S = Object.fromEntries(Object.entries(IRREGULAR_S2P).map(([s,p]) => [p, s]));

function singularizeLastWord(s){
  const w = s.toLowerCase().trim().split(/\s+/);
  if (!w.length) return s;
  let last = w[w.length - 1];

  // Irregular plural → singular first
  if (IRREGULAR_P2S && IRREGULAR_P2S[last]) {
    w[w.length - 1] = IRREGULAR_P2S[last];
    return w.join(" ");
  }

  // 🚫 do NOT strip 's' if the word ends with 'is' (axis, basis, analysis, thesis, …)
  if (/is$/.test(last)) {
    return w.join(" ");
  }

  if (last.endsWith("ies")) last = last.replace(/ies$/, "y");
  else if (/(?:[sxz]|ch|sh)es$/.test(last)) last = last.replace(/es$/, "");
  else if (last.endsWith("s") && !last.endsWith("ss")) last = last.replace(/s$/, "");
  w[w.length - 1] = last;
  return w.join(" ");
}


function pluralizeLastWord(s){
  const parts = s.toLowerCase().trim().split(/\s+/);
  if (!parts.length) return s;
  let last = parts[parts.length - 1];

  // Irregular singular → plural first (axis→axes, analysis→analyses, …)
  if (IRREGULAR_S2P[last]) {
    parts[parts.length - 1] = IRREGULAR_S2P[last];
    return parts.join(" ");
  }

  // Regular rules
  if (/[^aeiou]y$/.test(last)) last = last.replace(/y$/, "ies");
  else if (/(?:[sxz]|ch|sh)$/.test(last)) last = last + "es";
  else if (!/s$/.test(last)) last = last + "s";

  parts[parts.length - 1] = last;
  return parts.join(" ");
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

        // Build candidates: explicit id, base slug, singularized last word, pluralized last word
        const rawSing = singularizeLastWord(raw);
        const rawPlur = pluralizeLastWord(raw);

        const candidates = Array.from(new Set([
          slugFromHref,
          slugify(raw),
          slugify(rawSing),
          slugify(rawPlur),
        ].filter(Boolean)));

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
