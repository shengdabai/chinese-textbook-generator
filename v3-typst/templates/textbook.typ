#import "lib/chinese.typ": *
#import "lib/vocab-table.typ": *

#let accent = rgb(book-color)

#set document(
  title: book-title + " — " + book-subtitle,
  author: "Tony Sheng",
)
#set page(
  paper: "a4",
  margin: (x: 18mm, y: 20mm),
  numbering: "1",
  header: context {
    if counter(page).get().first() > 3 {
      set text(size: 8pt, fill: rgb("#667085"))
      [Z Turns Chinese — #book-title #h(1fr) #book-subtitle]
      line(length: 100%, stroke: 0.5pt + rgb("#d7deea"))
    }
  },
  footer: context {
    if counter(page).get().first() > 3 {
      set text(size: 8pt, fill: rgb("#667085"))
      line(length: 100%, stroke: 0.5pt + rgb("#d7deea"))
      [© 2026 Z Turns Chinese. All rights reserved.]
      h(1fr)
      counter(page).display("1")
    }
  },
)
#set par(leading: 1.8em)
#setup-chinese()

// ── Heading styles ─────────────────────────────────────────────────────────

#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  block(above: 0em, below: 1.5em)[
    #block(
      fill: accent,
      width: 100%,
      inset: (x: 14pt, y: 10pt),
      radius: (top-left: 4pt, top-right: 4pt),
    )[
      #set text(size: 22pt, weight: "bold", fill: white)
      #it.body
    ]
  ]
}

#show heading.where(level: 2): it => {
  block(above: 1.5em, below: 0.6em)[
    #set text(size: 15pt, weight: "bold", fill: accent)
    #it.body
    #line(length: 100%, stroke: 1pt + accent.lighten(60%))
  ]
}

#show heading.where(level: 3): it => {
  block(above: 1em, below: 0.4em)[
    #box(fill: accent, width: 4pt, height: 1em)
    #h(0.4em)
    #set text(size: 12pt, weight: "bold")
    #it.body
  ]
}

// ── Code blocks ─────────────────────────────────────────────────────────────

#show raw.where(block: true): it => block(
  fill: rgb("#f5f5f5"),
  inset: 10pt,
  radius: 4pt,
  width: 100%,
  text(font: ("JetBrains Mono", "PingFang SC"), size: 9pt, it),
)

// ── Cover page ──────────────────────────────────────────────────────────────

#page(
  header: none,
  footer: none,
  numbering: none,
  margin: (x: 0mm, y: 0mm),
  background: [
    #block(fill: accent, width: 100%, height: 45%)[]
    #block(fill: white, width: 100%, height: 55%)[]
  ],
)[
  #place(top + center, dy: 45% * 0.45)[
    #text(size: 80pt, weight: "bold", fill: white.transparentize(30%))[#book-number]
  ]
  #place(top + center, dy: 50%)[
    #block(width: 100%, inset: (x: 20mm))[
      #align(center)[
        #v(2cm)
        #text(size: 30pt, weight: "bold", fill: rgb("#1a1a1a"))[#book-title]
        #v(0.5cm)
        #text(size: 18pt, fill: accent)[#book-subtitle]
        #v(1.2cm)
        #line(length: 50%, stroke: 2pt + accent)
        #v(1cm)
        #text(size: 12pt, fill: rgb("#667085"))[Tony Sheng]
        #v(0.3cm)
        #text(size: 11pt, fill: rgb("#aaaaaa"))[zturnsgo.com]
      ]
    ]
  ]
]

// ── Copyright page ──────────────────────────────────────────────────────────

#page(
  header: none,
  footer: none,
  numbering: none,
)[
  #v(2cm)
  #set text(size: 9pt, fill: rgb("#555555"))
  #set par(leading: 1.4em, first-line-indent: 0em)
  #align(left)[
    *#book-title*\
    #book-subtitle\
    \
    Author: Tony Sheng\
    Website: zturnsgo.com\
    \
    © 2026 Z Turns Chinese. All rights reserved.\
    No part of this publication may be reproduced, distributed, or transmitted
    in any form or by any means without the prior written permission of the
    publisher, except in the case of brief quotations embodied in critical
    reviews and certain other noncommercial uses permitted by copyright law.\
    \
    For permissions, contact: #link("mailto:tony@zturnsgo.com")[tony\@zturnsgo.com]
  ]
]

// ── Table of Contents ────────────────────────────────────────────────────────

#outline(title: [目录 · Contents], indent: auto)
#pagebreak()

// ── Body (injected below) ────────────────────────────────────────────────────
