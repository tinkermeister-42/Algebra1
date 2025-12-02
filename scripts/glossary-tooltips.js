// glossary-tooltips.js — load glossary.json and attach math-aware tooltips

// ---------- Slug + path helpers ----------

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
  try {
    const r = await fetch(url, { method: "HEAD", cache: "no-store" });
    return r.ok;
  } catch {
    return false;
  }
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
  const offset = document
    .querySelector('meta[name="quarto:offset"]')
    ?.getAttribute("content");

  if (offset){
    const u = new URL(
      offset.replace(/\/?$/, "/") + "search.json" + ts,
      document.baseURI
    ).href;
    if (await headOk(u)) return new URL(offset, document.baseURI).pathname;
  }

  for (const dir of ancestorDirs()){
    if (await headOk(`${dir}search.json${ts}`)) return dir;
  }

  if (await headOk(`/search.json${ts}`)) return "/";
  return null;
}

// ---------- Encoding / JSON repair helpers ----------

function fixMojibake(txt){
  const map = new Map([
    ["â€œ","“"], ["â€\x9c","“"], ["â€\x9d","”"], ["â€","”"],
    ["â€˜","‘"], ["â€™","’"], ["â€“","–"], ["â€”","—"],
    ["â€¦","…"], ["â€¢","•"], ["â€","”"], ["Â",""], ["Ã—","×"]
  ]);
  for (const [bad, good] of map){
    txt = txt.split(bad).join(good);
  }
  return txt;
}

function decodeOctalEscapes(txt){
  return txt.replace(/\\([0-7]{1,3})/g, (_, oct) => {
    try {
      return String.fromCharCode(parseInt(oct, 8));
    } catch {
      return _;
    }
  });
}

async function loadGlossaryJson(root){
  const url = `${root}glossary.json?ts=${Date.now()}`;
  console.debug("[glossary] loading:", url);
  const r = await fetch(url, { cache: "no-store" });
  if (!r.ok){
    console.error("[glossary] HTTP", r.status, r.statusText);
    return null;
  }

  const raw = await r.text();
  try {
    return JSON.parse(raw);
  } catch (e1){
    let repaired = fixMojibake(raw);
    repaired = decodeOctalEscapes(repaired);
    try {
      return JSON.parse(repaired);
    } catch (e2){
      console.error("[glossary] JSON parse failed. First 200 chars:", raw.slice(0, 200));
      console.error("[glossary] After repair:", repaired.slice(0, 200));
      return null;
    }
  }
}

// ---------- MathJax v3 pre-render: $...$ -> <mjx-container>... ----------

async function renderMathInStringToHTML(text){
  // If MathJax v3 isn't ready, just return the original string
  if (
    typeof window.MathJax === "undefined" ||
    !MathJax.startup ||
    !MathJax.startup.promise ||
    typeof MathJax.tex2chtmlPromise !== "function"
  ){
    return text;
  }

  // Wait for MathJax to finish startup once
  await MathJax.startup.promise;

  const re = /\$(.+?)\$/g; // simple non-greedy inline math matcher
  let result = "";
  let lastIndex = 0;
  let match;

  while ((match = re.exec(text)) !== null){
    const before = text.slice(lastIndex, match.index);
    const tex = match[1];

    result += before;

    try {
      const node = await MathJax.tex2chtmlPromise(tex, { display: false });
      result += node.outerHTML;
    } catch (e){
      console.error("[glossary] tex2chtmlPromise error:", e);
      // fall back to raw TeX if something goes wrong
      result += "$" + tex + "$";
    }

    lastIndex = re.lastIndex;
  }

  result += text.slice(lastIndex);
  return result;
}

// ---------- Wire up tooltips once DOM is ready ----------

document.addEventListener("DOMContentLoaded", async () => {
  const root = await detectSiteRoot();
  if (!root){
    console.error("🔥 glossary: could not detect site root.");
    return;
  }

  const glossary = await loadGlossaryJson(root);
  if (!glossary){
    console.error("🔥 glossary: unable to load/parse glossary.json");
    return;
  }

  const hasTippy = typeof window.tippy === "function";
  if (!hasTippy){
    console.warn("[glossary] tippy() not found; tooltips will be disabled.");
  }

  document.querySelectorAll(".glossary-link").forEach(link => {
    const href = link.getAttribute("href") || "";
    const m = href.match(/#glossary-([^#?]+)/);
    const slugFromHref = m ? m[1] : null;

    const raw = link.dataset.term || link.textContent || "";
    const key = link.dataset.slug || slugFromHref || slugify(raw);

    const def = glossary[key];
    if (!def) return;

    if (!hasTippy){
      return; // nothing more we can do
    }

    // Build tooltip HTML (with TeX still as $...$)
    const baseHtml = `<strong>${raw}</strong><br>${def}`;

    // Use an async IIFE so we can await MathJax pre-render
    (async () => {
      const renderedHtml = await renderMathInStringToHTML(baseHtml);

      tippy(link, {
        content: renderedHtml,
        allowHTML: true,
        theme: "light-border",
        placement: "top",
        delay: [100, 100],
        maxWidth: 300,
        interactive: true
      });
    })();
  });
});
