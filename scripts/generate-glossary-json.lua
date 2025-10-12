-- scripts/generate-glossary-json.lua
-- Minimal generator: no plural logic, no alternates, no irregulars.
-- ONE entry per H3 glossary term:
--   If H3 has {#glossary-<id>} use <id> exactly.
--   Else slugify the heading text as-is.

local map = {}
local current = nil
local captured = false

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

local function push(slug, def)
  if slug and slug ~= "" then map[slug] = def end
end

local function add_term(term, def)
  local text, explicit = "", nil
  if type(term) == "table" then
    text = to_str(term.text)
    explicit = term.slug
  else
    text = to_str(term)
  end

  local key
  if explicit and explicit ~= "" then
    key = explicit:lower():gsub("[_%s]+","-"):gsub("-+","-")
  else
    key = slugify_words(text)
  end
  if key ~= "" then push(key, def) end
end

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
    add_term(current, pandoc.utils.stringify(el.content))
    captured = true
  end
end

function Plain(el)
  if current and not captured then
    add_term(current, pandoc.utils.stringify(el))
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
