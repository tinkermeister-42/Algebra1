local function h2(title, id, classes)
  classes = classes or {}
  return pandoc.Header(
    2,
    pandoc.Inlines(title),
    pandoc.Attr(id or "", classes)
  )
end

return {
  practice = function(args, kwargs, meta)
    return h2("✍️ Practice On Your Own", "practice", {"unnumbered", "pagebreak-before"})
  end,

  learn = function(args, kwargs, meta)
    return h2("👥 Learn Together", "learn", {"unnumbered"})
  end,

  warmup = function(args, kwargs, meta)
    return h2("🔥 Warm Up", "warmup", {"unnumbered"})
  end,

  interact = function(args, kwargs, meta)
    return h2("▶️ Interactive Learning", "interactive", {"unnumbered"})
  end
}
