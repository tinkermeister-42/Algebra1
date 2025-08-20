-- scripts/generate-glossary-json.lua
local map = {}
local current = nil
local captured = false

local function to_str(x) return type(x)=="string" and x or pandoc.utils.stringify(x or "") end
local function norm_spaces(s) s=to_str(s):gsub("%s+"," "):gsub("^%s+",""):gsub("%s+$",""); return s end
local function norm_text(s)
  s = norm_spaces(s):lower():gsub("&","and")
  s = s:gsub("[%p%c]","")
  return s
end
local function slugify_words(s)
  s = norm_text(s):gsub("%s+","-"):gsub("-+","-")
  return s
end
local function words_from(s)
  s = norm_text(s); local t = {}; for w in s:gmatch("%S+") do t[#t+1]=w end; return t
end
local function singular_last(s)
  local w = words_from(s); if #w==0 then return "" end
  local last = w[#w]
  if last:match("ies$") then last=last:gsub("ies$","y")
  elseif last:match("(s|x|z)es$") or last:match("ch(es)$") or last:match("sh(es)$") then last=last:gsub("es$","")
  elseif last:match("s$") and not last:match("ss$") then last=last:gsub("s$","") end
  w[#w]=last; return table.concat(w," ")
end
local function plural_last(s)
  local w = words_from(s); if #w==0 then return "" end
  local last = w[#w]
  if last:match("[^aeiou]y$") then last=last:gsub("y$","ies")
  elseif last:match("(s|x|z)$") or last:match("ch$") or last:match("sh$") then last=last.."es"
  elseif not last:match("s$") then last=last.."s" end
  w[#w]=last; return table.concat(w," ")
end

local function push(slug, def) if slug and slug~="" then map[slug]=def end end
local function push_variants(slug, def)
  push(slug, def)                                   -- hyphen
  push((slug:gsub("-", "_")), def)                  -- underscore alias
end

local function add_term_variants(term, def)
  local text, explicit = "", nil
  if type(term)=="table" then text=to_str(term.text); explicit=term.slug else text=to_str(term) end

  -- normalize explicit id -> lower + hyphens; else derive from text
  local base = explicit and explicit:lower():gsub("[_%s]+","-"):gsub("-+","-") or slugify_words(text)
  if base=="" then return end

  -- base + singular/plural keys (and their underscore aliases)
  push_variants(base, def)
  push_variants(slugify_words(singular_last(text)), def)
  push_variants(slugify_words(plural_last(text)), def)
end

function Header(el)
  if el.level==3 then
    captured=false
    local text = pandoc.utils.stringify(el.content)
    local id = el.identifier or (el.attr and el.attr.identifier) or ""
    if id:match("^glossary%-") then
      current = { text = text, slug = id:gsub("^glossary%-","") }
    else
      current = text
    end
  end
end

function Para(el)
  if current and not captured then add_term_variants(current, pandoc.utils.stringify(el.content)); captured=true end
end
function Plain(el)
  if current and not captured then add_term_variants(current, pandoc.utils.stringify(el)); captured=true end
end

function Pandoc(doc)
  local f = assert(io.open("glossary.json","w")); f:write("{\n")
  local keys = {}; for k,_ in pairs(map) do keys[#keys+1]=k end
  table.sort(keys)
  for i,k in ipairs(keys) do if i>1 then f:write(",\n") end; f:write(string.format('  %q: %q', k, map[k])) end
  f:write("\n}\n"); f:close(); return nil
end
