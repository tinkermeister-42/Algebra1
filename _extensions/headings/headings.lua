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

return {
  ["practice"] = function(args, kwargs, meta)
    return raw_block_for_heading("✍️ Practice On Your Own")
  end,
  ["learn"] = function(args, kwargs, meta)
    return raw_block_for_heading("👥 Learn Together")
  end,
  ["warmup"] = function(args, kwargs, meta)
    return raw_block_for_heading("🔥 Warm-Up")
  end
}
