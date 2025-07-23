local glossary = {}
local current_term = nil

function Header(el)
  if el.level == 3 then
    current_term = pandoc.utils.stringify(el.content):lower()
    glossary[current_term] = nil
  end
end

function Para(el)
  if current_term and glossary[current_term] == nil then
    glossary[current_term] = pandoc.utils.stringify(el.content)
  end
end

function Pandoc(doc)
  local f = io.open("glossary.json", "w")
  f:write("{\n")
  local first = true
  for term, def in pairs(glossary) do
    if not first then f:write(",\n") end
    first = false
    f:write(string.format('  %q: %q', term, def))
  end
  f:write("\n}\n")
  f:close()
  return nil
end
