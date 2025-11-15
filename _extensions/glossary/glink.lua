-- glink.lua — stable: single positional OR keyword overrides
-- Supports:
--   {{< glink axis >}}                         -- simple: display="axis", slug="axis"
--   {{< glink "coordinate plane" >}}           -- simple: display="coordinate plane", slug="coordinate-plane"
--   {{< glink slug="axis" text="axes" >}}      -- override display text, keep slug
--   {{< glink text="coordinate plane" >}}      -- display given; slug auto from text

local function slugify(s)
  s = string.lower(s or "")
  s = s:gsub("[^a-z0-9]+","-")
  s = s:gsub("^-+",""):gsub("-+$","")
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

    -- Prefer named params when present
    local display = to_text(kwargs["text"] or kwargs["label"] or kwargs["term"])
    local slug    = to_text(kwargs["slug"])

    -- Fall back to single positional for the common case
    if (not display or display == "") and #args >= 1 then
      display = to_text(args[1])
    end

    -- If still nothing, fail loudly
    if not display or display == "" then
      return pandoc.Span({ pandoc.Str("{{glink:missing-term}}") }, { class = "glink-error" })
    end

    if not slug or slug == "" then
      slug = slugify(display)
    end

    local href = "#glossary-" .. slug
    local attr = {
      class = "glossary-link",
      ["data-slug"] = slug,
      ["data-term"] = display,
      ["data-original-href"] = href,
      href = href
    }

    return pandoc.Link(display, "", "", attr)
  end
}
