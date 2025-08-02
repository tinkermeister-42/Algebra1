function glink(args, kwargs)
  if #args == 0 then
    return pandoc.Str("[MISSING_TERM]")
  end

  local original_term = table.concat(args, " ")
  local term = original_term:lower()

  -- Exception list: keep these as-is
  local no_singularize = {
    ["order of operations"] = true,
    ["parentheses"] = true,
    ["positive numbers"] = true,
    ["calculus"] = true
  }

  -- Irregular plural → singular map
  local irregulars = {
    ["indices"] = "index",
    ["vertices"] = "vertex",
    ["children"] = "child",
    ["men"] = "man",
    ["women"] = "woman",
    ["data"] = "datum"
  }

  -- Start with the original slug
  local slug = term:gsub("%s+", "-")
  local base_href = "/glossary.html#glossary-"
  local href = base_href .. slug

  -- Apply singularization only if not on the exception list
  if not no_singularize[term] then
    local singular_term = irregulars[term] or term:gsub("([^s])s$", "%1")
    local singular_slug = singular_term:gsub("%s+", "-")

    -- Only use singular version if different from original
    if singular_slug ~= slug then
      slug = singular_slug
      href = base_href .. slug
      term = singular_term
    end
  end

  return pandoc.Link(pandoc.Str(original_term), href, "", {
    class = "glossary-link",
    ["data-term"] = term,
    ["data-original-term"] = original_term
  })
end
