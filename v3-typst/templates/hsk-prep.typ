#import "lib/chinese.typ": *
#import "lib/colors.typ": *
#import "lib/vocab-table.typ": *
#import "lib/ruby.typ": *

#let accent = hsk-colors.at(hsk-level, default: rgb("#1565C0"))

#set document(
  title: "Z Turns Chinese — HSK " + hsk-level + " 备考指南",
  author: "Tony Sheng",
)
#set page(
  paper: "a4",
  margin: (x: 15mm, y: 18mm),
  numbering: "1",
  header: context {
    set text(size: 8pt, fill: rgb("#667085"))
    [Z Turns Chinese #h(1fr) HSK #hsk-level 备考指南]
    line(length: 100%, stroke: 0.5pt + rgb("#d7deea"))
  },
  footer: context {
    set text(size: 8pt, fill: rgb("#667085"))
    line(length: 100%, stroke: 0.5pt + rgb("#d7deea"))
    [© 2026 Z Turns Chinese. All rights reserved.]
    h(1fr)
    counter(page).display("1")
  },
)
#set par(leading: 1.8em)
#setup-chinese()

#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  block(above: 2em, below: 1em)[
    #set text(size: 20pt, weight: "bold", fill: accent)
    #it.body
    #line(length: 100%, stroke: 2pt + accent)
  ]
}
#show heading.where(level: 2): it => {
  block(above: 1.5em, below: 0.6em)[
    #set text(size: 14pt, weight: "bold", fill: accent)
    #it.body
  ]
}
#show heading.where(level: 3): it => {
  block(above: 1em, below: 0.4em)[
    #rect(fill: accent, width: 3pt, height: 1em)
    #h(0.4em)
    #set text(size: 11.5pt, weight: "bold")
    #it.body
  ]
}

#show raw.where(block: true): it => block(
  fill: rgb("#f5f5f5"),
  inset: 10pt,
  radius: 4pt,
  width: 100%,
  text(font: ("JetBrains Mono", "PingFang SC"), size: 9pt, it),
)

#align(center)[
  #v(4cm)
  #text(size: 11pt, fill: rgb("#667085"))[Z TURNS CHINESE]
  #v(0.5cm)
  #text(size: 36pt, weight: "bold", fill: accent)[HSK #hsk-level]
  #v(0.3cm)
  #text(size: 18pt, fill: rgb("#333333"))[备考指南]
  #v(0.3cm)
  #text(size: 14pt, fill: rgb("#667085"))[#hsk-title]
  #v(1cm)
  #line(length: 60%, stroke: 2pt + accent)
  #v(1cm)
  #text(size: 11pt, fill: rgb("#667085"))[Tony Sheng]
  #pagebreak()
]

#outline(title: "目录", indent: auto)
#pagebreak()
