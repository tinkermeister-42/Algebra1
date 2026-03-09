-- glink.lua
-- {{< glink axis >}}                        -- href=#glossary-axis, display="axis"
-- {{< glink "like terms" >}}                -- href=#glossary-like_terms, display="like terms"
-- {{< glink slug="axis" text="axes" >}}     -- href=#glossary-axis, display="axes"

local function normalize(s)
  s = string.lower(s or "")
  s = s:gsub("%s+", "-")
  return s
end

local function to_text(v)
  if v == nil then return nil end
  if type(v) == "string" then return v end
  return pandoc.utils.stringify(v)
end

return {
  ['glink'] = function(args, kwargs, meta)
    kwargs = kwargs or {}

    local slug    = to_text(kwargs["slug"])
    local display = to_text(kwargs["text"] or kwargs["label"] or kwargs["term"])

    if #args >= 1 then
      local positional = to_text(args[1])
      if not slug    or slug    == "" then slug    = normalize(positional) end
      if not display or display == "" then display = positional end
    end

    if not display or display == "" then
      return pandoc.Span({ pandoc.Str("{{glink:missing-term}}") }, pandoc.Attr("", { "glink-error" }, {}))
    end

    if not slug or slug == "" then
      slug = normalize(display)
    end

    local href = "#glossary-" .. slug
    local attr = {
      class              = "glossary-link",
      ["data-slug"]      = slug,
      ["data-term"]      = display,
      ["data-original-href"] = href,
      href               = href
    }

    return pandoc.Link({ pandoc.Str(display) }, href, "", attr)
  end
}