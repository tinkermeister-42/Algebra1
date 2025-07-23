function glink(args, kwargs)
  if #args == 0 then
    return pandoc.Str("[MISSING_TERM]")
  end

  local term = table.concat(args, " ")
  local slug = term:lower():gsub("%s+", "-")

  local href = "/glossary.html#glossary-" .. slug

  return pandoc.Link(pandoc.Str(term), href, "", {
    class = "glossary-link",
    ["data-term"] = term
  })
end
