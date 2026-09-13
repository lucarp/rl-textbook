#!/usr/bin/env python3
"""Render one section (an HTML fragment from a chapter) as a standalone PDF, using the
book's own CSS, MathJax, and Paged.js pipeline so it looks exactly like the book.

Usage: python3 build_section.py <fragment.html> <out.pdf> [--title "..."] [--note "..."] [--id chNN]
       python3 build_section.py chapters/chNN-*.html <out.pdf> --whole-chapter   (a complete chapter file)

The fragment is wrapped in <section class="chapter"> under an <h1> (which feeds the running
header), preceded by an italic excerpt note. Intermediate HTML is written next to book.html
(it must live in build/ so ../assets/ resolves).
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402  (HEAD, FOOT, ROOT; importing does not run its main())


def arg(flag, default):
    if flag in sys.argv:
        return sys.argv[sys.argv.index(flag) + 1]
    return default


def main() -> None:
    frag_path = Path(sys.argv[1])
    out_pdf = Path(sys.argv[2]).resolve()
    title = arg("--title", "Chapter 4 &mdash; RL as weighted behavior cloning")
    note = arg("--note", "Standalone excerpt of Section 4.4. References to Sections 4.1&ndash;4.3, "
                         "4.5&ndash;4.6 and to Chapter 3 point into the full book.")
    sec_id = arg("--id", "ch04")

    frag = frag_path.read_text()
    # A standalone document must not open with a forced page break (blank first page).
    extra = "<style>section.chapter { break-before: auto; }\n" \
            "p.excerpt-note { font-family: \"Noto Sans\", sans-serif; font-size: 8.6pt; color: #666; margin: -0.3em 0 1.2em 0; }</style>\n"
    head = build.HEAD.replace("</head>", extra + "</head>", 1)
    if "--whole-chapter" in sys.argv:
        # The input is a complete chapter file (already a <section class="chapter"> with its own <h1>).
        body = frag + "\n"
    else:
        body = (f'<section class="chapter" id="{sec_id}">\n<h1>{title}</h1>\n'
                f'<p class="excerpt-note">{note}</p>\n{frag}\n</section>\n')
    html = head + body + build.FOOT

    out_html = build.ROOT / "build" / (out_pdf.stem + ".html")
    out_html.write_text(html)
    print(f"wrote {out_html} ({out_html.stat().st_size} bytes)")
    subprocess.run(["node", str(build.ROOT / "build" / "render.js"), str(out_html), str(out_pdf)],
                   check=True, timeout=660)
    info = subprocess.run(["pdfinfo", str(out_pdf)], capture_output=True, text=True).stdout
    pages = [l for l in info.splitlines() if l.startswith("Pages")]
    print(f"rendered {out_pdf} — {pages[0] if pages else '?'}")


if __name__ == "__main__":
    main()
