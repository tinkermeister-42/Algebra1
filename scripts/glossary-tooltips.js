// glossary-tooltips.js — robust loader: fixes mojibake + octal escapes if needed

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

async function headOk(url){
  try { const r = await fetch(url, { method: "HEAD", cache: "no-store" }); return r.ok; }
  catch { return false; }
}

function ancestorDirs(){
  const path = location.pathname.replace(/\/[^/]*$/, "/");
  const parts = path.split("/").filter(Boolean);
  const dirs = [];
  for (let i = parts.length; i >= 0; i--){
    const p = "/" + parts.slice(0, i).join("/") + (i ? "/" : "");
    dirs.push(p);
  }
  return Array.from(new Set(dirs));
}

async function detectSiteRoot(){
  const ts = `?ts=${Date.now()}`;
  const offset = document.querySelector('meta[name="quarto:offset"]')?.getAttribute('content');
  if (offset){
    const u = new URL(offset.replace(/\/?$/, "/") + "search.json" + ts, document.baseURI).href;
    if (await headOk(u)) return new URL(offset, document.baseURI).pathname;
  }
  for (const dir of ancestorDirs()){
    if (await headOk(`${dir}search.json${ts}`)) return dir;
  }
  if (await headOk(`/search.json${ts}`)) return "/";
  return null;
}

// --- Encoding/escape repair helpers ---
function fixMojibake(txt){
  // Common UTF-8→CP1252 mojibake mappings
  const map = new Map([
    ["â€œ","“"], ["â€\x9c","“"], ["â€\x9d","”"], ["â€","”"], ["â€˜","‘"], ["â€™","’"],
    ["â€“","–"], ["â€”","—"], ["â€¦","…"], ["â€¢","•"], ["â€","”"], ["Â",""], ["Ã—","×"]
  ]);
  for (const [bad, good] of map) txt = txt.split(bad).join(good);
  return txt;
}
function decodeOctalEscapes(txt){
  // Replace \ooo (octal) with the corresponding Unicode char; JSON disallows octal
  return txt.replace(/\\([0-7]{1,3})/g, (_, oct) => {
    try { return String.fromCharCode(parseInt(oct, 8)); }
    catch { return _; }
  });
}

async function loadGlossaryJson(root){
  const url = `${root}glossary.json?ts=${Date.now()}`;
  console.debug("[glossary] loading:", url);
  const r = await fetch(url, { cache: "no-store" });
  if (!r.ok){ console.error("[glossary] HTTP", r.status, r.statusText); return null; }
  const raw = await r.text();
  try {
    return JSON.parse(raw);
  } catch (e1){
    // Try to repair encoding and illegal escapes
    let repaired = fixMojibake(raw);
    repaired = decodeOctalEscapes(repaired);
    try {
      return JSON.parse(repaired);
    } catch (e2){
      console.error("[glossary] JSON parse failed. First 200 chars:", raw.slice(0,200));
      console.error("[glossary] After repair:", repaired.slice(0,200));
      return null;
    }
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const root = await detectSiteRoot();
  if (!root){ console.error("🔥 glossary: could not detect site root."); return; }

  const glossary = await loadGlossaryJson(root);
  if (!glossary){ console.error("🔥 glossary: unable to load/parse glossary.json"); return; }

  document.querySelectorAll(".glossary-link").forEach(link => {
    const href = link.getAttribute("href") || "";
    const m = href.match(/#glossary-([^#?]+)/);
    const slugFromHref = m ? m[1] : null;

    const raw = link.dataset.term || link.textContent || "";
    const key = slugFromHref || slugify(raw);

    const def = glossary[key];
    if (!def) return;

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
