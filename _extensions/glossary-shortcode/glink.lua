function glink(args, kwargs)
  if #args == 0 then
    return pandoc.Str("[MISSING_TERM]")
  end

  local original_term = table.concat(args, " ")
  local term = original_term:lower()

  -- Try to generate singular form if plural
  if term:match("s$") then
    local singular = term:gsub("s$", "") -- basic singularization
    term = singular
  end

  -- Slugify (e.g., "negative number" → "negative-number")
  local slug = term:gsub("%s+", "-")

  local href = "/glossary.html#glossary-" .. slug

  return pandoc.Link(pandoc.Str(original_term), href, "", {
    class = "glossary-link",
    ["data-term"] = term
  })
end
