-- Return format-appropriate raw blocks for HTML or PDF
local function raw_block_for_heading(text)
  if quarto.doc.isFormat("html") then
    return pandoc.RawBlock("html", '<h2 class="unnumbered">' .. text .. "</h2>")
  elseif quarto.doc.isFormat("pdf") then
    return pandoc.RawBlock("tex", "\\section*{" .. text .. "}")
  else
    -- fallback: a real header node (works for Word, etc.)
    return pandoc.Header(2, pandoc.Inlines(text))
  end
end


local function heading(level, title)
  return pandoc.Header(level, title)
end

local function heading_with_pagebreak(level, title)
  -- add a CSS class that we will target in styles
  return pandoc.Header(level, title, pandoc.Attr("", {"pagebreak-before"}))
end

return {
  practice = function(args, kwargs, meta)
    -- H2 with a class that triggers a page break in CSS
    return heading_with_pagebreak(2, "✍️ Practice On Your Own")
  end,

  learn = function(args, kwargs, meta)
    return heading(2, "👥 Learn Together")
  end,

  warmup = function(args, kwargs, meta)
    return heading(2, "🔥 Warm-Up")
  end,

  interact = function(args, kwargs, meta)
    return heading(2, "▶️ Interactive Learning")
  end
}

