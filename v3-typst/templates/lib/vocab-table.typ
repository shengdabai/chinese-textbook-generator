#let vocab-table(rows) = {
  set text(size: 9pt)
  table(
    columns: (auto, auto, 1fr),
    fill: (_, y) => if y == 0 { rgb("#f0f4f8") } else if calc.odd(y) { white } else { rgb("#fafbfc") },
    stroke: 0.5pt + rgb("#d7deea"),
    table.header(
      table.cell(fill: rgb("#e8edf5"))[*汉字*],
      table.cell(fill: rgb("#e8edf5"))[*拼音*],
      table.cell(fill: rgb("#e8edf5"))[*释义*],
    ),
    ..rows
  )
}

#let vocab-table-extended(rows) = {
  set text(size: 8.5pt)
  table(
    columns: (auto, auto, auto, auto, 1.6fr, 1.6fr, 1fr),
    fill: (_, y) => if y == 0 { rgb("#f0f4f8") } else if calc.odd(y) { white } else { rgb("#fafbfc") },
    stroke: 0.5pt + rgb("#d7deea"),
    table.header(
      table.cell(fill: rgb("#e8edf5"))[*汉字*],
      table.cell(fill: rgb("#e8edf5"))[*拼音*],
      table.cell(fill: rgb("#e8edf5"))[*词性*],
      table.cell(fill: rgb("#e8edf5"))[*释义*],
      table.cell(fill: rgb("#e8edf5"))[*例句*],
      table.cell(fill: rgb("#e8edf5"))[*Pinyin*],
      table.cell(fill: rgb("#e8edf5"))[*English*],
    ),
    ..rows
  )
}

// 6-col vocab table for HSK 3-6: no pinyin example column
#let vocab-table-simple(rows) = {
  set text(size: 8.5pt)
  table(
    columns: (auto, auto, auto, auto, 1.8fr, 1.4fr),
    fill: (_, y) => if y == 0 { rgb("#f0f4f8") } else if calc.odd(y) { white } else { rgb("#fafbfc") },
    stroke: 0.5pt + rgb("#d7deea"),
    table.header(
      table.cell(fill: rgb("#e8edf5"))[*汉字*],
      table.cell(fill: rgb("#e8edf5"))[*拼音*],
      table.cell(fill: rgb("#e8edf5"))[*词性*],
      table.cell(fill: rgb("#e8edf5"))[*释义*],
      table.cell(fill: rgb("#e8edf5"))[*例句*],
      table.cell(fill: rgb("#e8edf5"))[*English*],
    ),
    ..rows
  )
}
