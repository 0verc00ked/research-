# Compile instructions — `india_pe_research_paper.tex`

This is a **single, self-contained** LaTeX source. There are **no external image files**, **no `.bib` file**, and **no shell-escape** required. All 12 charts and 5 diagrams are drawn natively with `pgfplots`/`tikz`; the bibliography is an in-document `longtable` (Appendix A).

## How to compile

Run `pdflatex` **twice** (the second pass resolves cross-references, the table of contents, and `longtable` column widths):

```sh
pdflatex india_pe_research_paper.tex
pdflatex india_pe_research_paper.tex
```

Output: `india_pe_research_paper.pdf`.

- No `bibtex`/`biber` step is needed (the bibliography is a typeset table, not a `.bib`).
- No `--shell-escape` is needed (no externalization, no `\write18`).
- A TeX Live 2021 or newer distribution (or MiKTeX) is recommended so that `pgfplots` `compat=1.18` is available.

### Alternative engines

`lualatex` or `xelatex` also work without changes (the source is plain T1/`lmodern` with `inputenc` UTF-8, and contains no raw non-ASCII bytes), but `pdflatex` is the intended/tested target. If you use `lualatex`/`xelatex`, the `inputenc` line is harmless.

## Packages used (all standard, in TeX Live / MiKTeX)

`inputenc` (utf8), `fontenc` (T1), `lmodern`, `geometry`, `parskip`, `microtype`,
`amsmath`, `amssymb`,
`booktabs`, `longtable`, `array`, `tabularx`, `ltablex`,
`graphicx`, `xcolor`, `float`, `pdflscape`, `caption`, `enumitem`, `csquotes`,
`fancyhdr`, `titlesec`,
`tikz`, `pgfplots` (with `\pgfplotsset{compat=1.18}`),
`hyperref` (loaded near-last), `url`.

TikZ libraries: `positioning`, `arrows.meta`, `shapes.geometric`, `shapes.misc`, `fit`, `backgrounds`, `calc`.

## Document structure

- **Front matter:** title page, abstract (~300 words), keywords, boxed five-level Evidence-Classification legend, provenance note.
- **Body:** Sections 1–16 mirror the source report (Executive Summary → Causal Analysis → Future Scenarios), then Recommendations (17), Master Findings Classification (18), Limitations (19), Cumulative FDI Context (20), and the Expanded Major-Transactions Database (21, in a `landscape` page).
- **Figures:** 12 `pgfplots` charts (CH1–CH12) and 5 TikZ/styled diagrams (DG1 five capital pools; DG2 IHH→Fortis/Gleneagles chain; DG3 GIC/AHH platform; DG4 sovereign/pension footprint map; DG5 concentration-vs-foreign-intensity gradient). Every figure is a captioned, labelled float with a source note.
- **Tables:** bed-ownership census, the "25% claim" denominator table, the consolidated CR/HHI table, the value-extraction scorecard, the FDI route/chronology table, the health-financing indicators table, the US-PE effect-sizes table, the cumulative-FDI table, the master-findings table, and the master timeline.
- **Appendix A — Sources Register:** a `longtable` rendering of all sources (repository artifacts L01–L07 and S01–S228), with ID, title, date, reliability, used-for and a click-through `\url`. This is the bibliography; every `[Sxx]` in the body maps here.
- **Appendix B — Evidence Dossiers:** the 21 themed dossier names under `research_2026-06/` (each `[D:name]` citation maps here).
- **Final Standard** statement.

## Notes / known-safe choices

- All money is written as `US\$…` / `Rs …`; all percentages as `…\%`; `R&D` as `R\&D`. No rupee/dash/arrow Unicode glyphs appear in the file (arrows are `$\rightarrow$`, dashes are `---`/`--`, `~` approximations are `$\sim$`).
- File/dossier names with underscores are wrapped in `\texttt{…}` with each `_` escaped, or escaped inline in `\cs{D:…}` citations.
- URLs in Appendix A are inside `\url{…}` and are intentionally **not** manually escaped (some contain `%`, which `\url` tolerates).
- The widest tables (Expanded Major-Transactions Database) are placed on a `landscape` page; the Sources Register and other wide tables use `tabularx`/fixed `p{}` column widths summing within `\textwidth` at 1-inch margins.
- The CH9 horizontal bar chart uses paren-free symbolic coordinate keys with display labels supplied via `yticklabels` (parentheses inside `pgfplots` coordinate names are avoided throughout to keep the coordinate parser happy).
