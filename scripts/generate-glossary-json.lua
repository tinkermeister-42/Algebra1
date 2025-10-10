-- scripts/generate-glossary-json.lua
-- Minimal, clean glossary JSON generator:
-- * Emits the base slug for each H3 glossary term.
-- * Optionally emits ONE irregular alternate when the LAST word is in the map (e.g., axis <-> axes).
-- * No generic plural/singular heuristics. No underscore aliases. No noisy variants.

local map = {}
local current = nil
local captured = false

-- Irregular singular <-> plural for LAST word only
local IRREGULAR_S2P = {
  axis = "axes",
  analysis = "analyses",
  basis = "bases",
  parenthesis = "parentheses",
  thesis = "theses",
  crisis = "crises",
  diagnosis = "diagnoses",
  hypothesis = "hypotheses",
  synthesis = "syntheses",
  synopsis = "synopses",
  ellipsis = "ellipses",
  oasis = "oases",
}
local IRREGULAR_P2S = {}
for s, p in pairs(IRREGULAR_S2P) do IRREGULAR_P2S[p] = s end

-- --- helpers ---
local function to_str(x)
  return type(x) == "string" and x or pandoc.utils.stringify(x or "")
end

local function norm_spaces(s)
  s = to_str(s):gsub("%s+", " "):gsub("^%s+", ""):gsub("%s+$", "")
  return s
end

local function norm_text(s)
  s = norm_spaces(s):lower():gsub("&", "and")
  s = s:gsub("[%p%c]", "")
  return s
end

local function slugify_words(s)
  s = norm_text(s):gsub("%s+", "-"):gsub("-+", "-")
  return s
end

local function words_from(s)
  s = norm_text(s)
  local t = {}
  for w in s:gmatch("%S+") do t[#t + 1] = w end
  return t
end

local function push(slug, def)
  if slug and slug ~= "" then map[slug] = def end
end

-- Replace only the last word in an already-normalized word list, then slugify
local function replace_last_word(words, new_last)
  local t = { table.unpack(words) }
  t[#t] = new_last
  return slugify_words(table.concat(t, " "))
end

local function add_term_variants(term, def)
  local text, explicit = "", nil
  if type(term) == "table" then
    text = to_str(term.text)
    explicit = term.slug
  else
    text = to_str(term)
  end

  -- Base slug: explicit id (normalized) wins; otherwise slugify header text
  local base = explicit and explicit:lower():gsub("[_%s]+", "-"):gsub("-+", "-") or slugify_words(text)
  if base == "" then return end

  -- Always push the base key
  push(base, def)

  -- Compute ONE irregular alternate if the LAST word qualifies
  local words = words_from(text)
  if #words == 0 then return end
  local last = words[#words]

  local alt_last = nil
  if IRREGULAR_S2P[last] then
    -- header last word is singular; add plural form
    alt_last = IRREGULAR_S2P[last]
  elseif IRREGULAR_P2S[last] then
    -- header last word is plural; add singular form
    alt_last = IRREGULAR_P2S[last]
  end

  if alt_last and alt_last ~= last then
    local alt_slug = replace_last_word(words, alt_last)
    if alt_slug ~= "" and alt_slug ~= base then
      push(alt_slug, def)
    end
  end
end

-- --- Pandoc callbacks ---
function Header(el)
  if el.level == 3 then
    captured = false
    local text = pandoc.utils.stringify(el.content)
    local id = el.identifier or (el.attr and el.attr.identifier) or ""
    if id:match("^glossary%-") then
      current = { text = text, slug = id:gsub("^glossary%-", "") }
    else
      current = text
    end
  end
end

function Para(el)
  if current and not captured then
    add_term_variants(current, pandoc.utils.stringify(el.content))
    captured = true
  end
end

function Plain(el)
  if current and not captured then
    add_term_variants(current, pandoc.utils.stringify(el))
    captured = true
  end
end

function Pandoc(doc)
  local f = assert(io.open("glossary.json", "w"))
  f:write("{\n")
  local keys = {}
  for k, _ in pairs(map) do keys[#keys + 1] = k end
  table.sort(keys)
  for i, k in ipairs(keys) do
    if i > 1 then f:write(",\n") end
    f:write(string.format('  %q: %q', k, map[k]))
  end
  f:write("\n}\n")
  f:close()
  return nil
end
