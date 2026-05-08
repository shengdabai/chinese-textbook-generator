#let py(zh, pinyin) = box(
  baseline: 0.1em,
  stack(
    dir: ttb,
    spacing: 0.1em,
    text(size: 0.55em, fill: rgb("#667085"), font: ("PingFang SC",), pinyin),
    zh,
  )
)
