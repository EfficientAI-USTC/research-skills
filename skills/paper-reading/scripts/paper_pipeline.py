"""Portable paper extraction, chunking and preview. Translation is done by the agent."""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import hashlib
import html
import json
import mimetypes
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen


def read(path):
    return Path(path).read_text(encoding="utf-8-sig")


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def save_json(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def soup(value):
    from bs4 import BeautifulSoup
    return BeautifulSoup(value, "html.parser")


def fetch(url):
    if urlparse(url).scheme not in {"http", "https"}:
        raise ValueError("Only HTTP(S) downloads are supported")
    req = Request(url, headers={"User-Agent": "paper-reading/2.0 (local research archive)"})
    with urlopen(req, timeout=45) as response:
        return response.read()


def local_asset(root, src):
    parsed = urlparse(src)
    if parsed.scheme or parsed.netloc:
        raise ValueError(f"Expected a local image: {src}")
    path = (Path(root) / unquote(parsed.path)).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError(f"Image path escapes paper directory: {src}")
    return path


def extract_html(args):
    out = Path(args.out).resolve()
    if (out / "extraction.json").exists():
        raise ValueError("Extraction exists; use a new output directory to preserve it")
    raw = read(args.file) if args.file else fetch(args.url).decode("utf-8")
    doc = soup(raw)
    body = doc.select_one("article.ltx_document") or doc.find("article") or doc.find("body")
    if body is None:
        raise ValueError("No article/body found; check for an error or access-denied page")
    out.mkdir(parents=True, exist_ok=True)
    write(out / "paper.html", raw)
    inventory = {"method": "html", "url": args.url, "images": [], "objects": [], "issues": []}
    for tag in body.select("script, style, nav, .ltx_page_header, .ltx_page_footer"):
        tag.decompose()

    inventory["math_tex"] = []
    for tag in body.find_all("math"):
        ann = tag.find("annotation", attrs={"encoding": "application/x-tex"})
        inventory["math_tex"].append(ann.get_text() if ann else tag.get("alttext", ""))

    # Equation layout tables are not data tables. Join their cells back into one
    # display, retaining the original TeX fragments and equation numbers.
    for table in list(body.select("table.ltx_equationgroup, table.ltx_equation")):
        if table.find_parent("table"):
            continue
        rows = []
        numbers = [x.get_text(strip=True).strip("()") for x in table.select(".ltx_tag_equation, .ltx_tag_equationgroup")]
        for row in table.find_all("tr"):
            cells = []
            for cell in row.find_all(["td", "th"], recursive=False):
                fragments = []
                for tag in cell.find_all("math"):
                    ann = tag.find("annotation", attrs={"encoding": "application/x-tex"})
                    tex = ann.get_text() if ann else tag.get("alttext")
                    if tex:
                        fragments.append(tex)
                    else:
                        inventory["issues"].append("Equation cell lacks TeX; verify PDF")
                if fragments:
                    cells.append(" ".join(fragments))
            if cells:
                row_text = " & ".join(cells)
                if len(numbers) > 1:
                    row_numbers = row.select(".ltx_tag_equation, .ltx_tag_equationgroup")
                    if row_numbers:
                        row_text += r"\qquad\text{" + row_numbers[0].get_text(strip=True) + "}"
                rows.append(row_text)
        if rows:
            tex = "\\begin{aligned}\n" + " \\\\\n".join(rows) + "\n\\end{aligned}"
            if len(numbers) == 1:
                tex += "\\tag{" + numbers[0] + "}"
            table.replace_with("\n\n$$\n" + tex + "\n$$\n\n")

    # MathML stores author's TeX; replacing outer math avoids duplicate alt text.
    for tag in list(body.find_all("math")):
        ann = tag.find("annotation", attrs={"encoding": "application/x-tex"})
        tex = ann.get_text() if ann else tag.get("alttext")
        if tex:
            display = tag.get("display") == "block" or tag.find_parent(class_="ltx_equation") is not None
            tag.replace_with(("$$\n" + tex + "\n$$") if display else "$" + tex + "$")
        else:
            inventory["issues"].append("MathML without TeX; verify against PDF")

    # Some LaTeXML tables use span rows/cells, including nested inline spans.
    for tag in body.select(".ltx_tabular"):
        if tag.name in {"span", "div"}:
            tag.name = "table"
    for tag in body.select(".ltx_thead, .ltx_tbody, .ltx_tfoot"):
        if tag.name in {"span", "div"}:
            tag.name = {"ltx_thead": "thead", "ltx_tbody": "tbody", "ltx_tfoot": "tfoot"}[next(c for c in tag.get("class", []) if c in {"ltx_thead", "ltx_tbody", "ltx_tfoot"})]
    for tag in body.select("span.ltx_tr"):
        tag.name = "tr"
    for tag in body.select("span.ltx_td, span.ltx_th"):
        tag.name = "th" if "ltx_th" in tag.get("class", []) else "td"
    for row in body.find_all("tr"):
        if row.find_parent("table") is None:
            container = row.parent.parent if row.parent.name in {"thead", "tbody", "tfoot"} else row.parent
            if container is not body:
                container.name = "table"
            else:
                inventory["issues"].append("Unwrapped table row; verify its layout against PDF")

    for i, tag in enumerate(body.select("img, object[data]"), 1):
        src = tag.get("src") or tag.get("data")
        if not src:
            continue
        try:
            if src.startswith("data:"):
                header, data = src.split(",", 1)
                payload = base64.b64decode(data) if ";base64" in header else unquote(data).encode()
                ext = mimetypes.guess_extension(header[5:].split(";")[0]) or ".png"
            else:
                ext = Path(urlparse(src).path).suffix.lower() or ".png"
                candidate = local_asset(Path(args.file).parent, src) if args.file and not urlparse(src).scheme and not src.startswith("/") else None
                payload = candidate.read_bytes() if candidate and candidate.is_file() else fetch(urljoin(args.url or "", src))
            if ext not in {".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".bmp"}:
                raise ValueError(f"Unsupported image extension {ext}; preserve via PDF crop")
            rel = f"images/figure_{i:03d}{ext}"
            target = out / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            inventory["images"].append({"source": src, "path": rel})
            tag.replace_with(f"\n\n![{tag.get('alt', '')}]({rel})\n\n")
        except Exception as exc:
            inventory["issues"].append(f"Image {src}: {exc}")
            tag.replace_with(f"\n\n[IMAGE MISSING: {src}]\n\n")

    for tag in body.select("figure, .ltx_equation, .ltx_theorem, .ltx_note"):
        caption = tag.find("figcaption")
        inventory["objects"].append({"id": tag.get("id"), "class": tag.get("class"),
                                     "caption": caption.get_text(" ", strip=True) if caption else ""})

    # Preserve notes rather than flattening LaTeXML superscripts into numbers.
    notes = []
    note_nodes = list(enumerate(list(body.select(".ltx_note")), 1))
    for i, tag in reversed(note_nodes):
        content = tag.select_one(".ltx_note_content")
        mark = tag.select_one(".ltx_note_mark")
        if content is None:
            continue
        note_id = f"note{i}"
        if mark and content.get_text(strip=True).startswith(mark.get_text(strip=True)):
            cm = content.select_one(".ltx_note_mark")
            if cm:
                cm.decompose()
        notes.append((i, f"[^{note_id}]: {content.get_text(' ', strip=True)}"))
        tag.replace_with(f"[^{note_id}]")

    def convert(node):
        if isinstance(node, str):
            return str(node)
        name = node.name
        children = lambda: "".join(convert(c) for c in node.children)
        if name == "table" and "ltx_equation" not in node.get("class", []):
            for t in node.find_all(True):
                if t.name not in {"table", "thead", "tbody", "tfoot", "tr", "td", "th", "caption", "colgroup", "col", "span", "b", "i", "em", "strong", "sub", "sup", "br", "a", "code"}:
                    t.unwrap()
            return "\n\n" + str(node) + "\n\n"
        if name and re.fullmatch(r"h[1-6]", name):
            level = 2 if "ltx_title_abstract" in node.get("class", []) else int(name[1])
            return "\n\n" + "#" * level + " " + re.sub(r"\s+", " ", children()).strip() + "\n\n"
        if name == "pre":
            return "\n\n```\n" + node.get_text() + "\n```\n\n"
        if name == "code":
            return "`" + node.get_text() + "`"
        if name == "span" and "ltx_font_bold" in node.get("class", []):
            return "**" + children() + "**"
        if name == "span" and "ltx_font_typewriter" in node.get("class", []):
            return "`" + children() + "`"
        if name in {"strong", "b", "em", "i"}:
            marker = "**" if name in {"strong", "b"} else "*"
            return marker + children() + marker
        if name in {"sup", "sub"}:
            return f"<{name}>" + children() + f"</{name}>"
        if name == "a":
            label = children()
            href = node.get("href", "")
            if href.startswith("#"):
                return label  # IDs change during Markdown conversion; preserve citation text.
            return f"[{label}]({urljoin(args.url or '', href)})" if href else label
        if name == "li":
            prefix = "- "
            for mark in node.select(".ltx_tag_item"):
                if mark.find_parent("li") is node:
                    mark.decompose()
            if node.parent.name == "ol":
                number = int(node.parent.get("start", 1)) + len(node.find_previous_siblings("li"))
                prefix = f"{number}. "
            return "\n" + prefix + children().strip().replace("\n", "\n    ") + "\n"
        if name == "br":
            return "\n"
        if name in {"p", "div", "section", "figure", "figcaption", "ul", "ol", "blockquote"}:
            return "\n\n" + children().strip() + "\n\n"
        return children()

    result = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", convert(body)).strip()
    if notes:
        result += "\n\n" + "\n\n".join(value for _, value in sorted(notes))
    write(out / "paper.html.md", result + "\n")
    inventory["tables"] = len(soup(result).find_all("table"))
    save_json(out / "extraction.json", inventory)
    print(json.dumps({"images": len(inventory["images"]), "tables": inventory["tables"],
                      "math_fragments": len(inventory["math_tex"]), "issues": inventory["issues"]}, ensure_ascii=False))


def extract_pdf(args):
    import pymupdf as fitz
    out = Path(args.out)
    if (out / "extraction.json").exists():
        raise ValueError("Extraction exists; use a new output directory to preserve it")
    out.mkdir(parents=True, exist_ok=True)
    source = Path(args.pdf).resolve()
    if source != (out / "source.pdf").resolve():
        shutil.copy2(source, out / "source.pdf")
    sections, blank = [], []
    (out / "pages").mkdir(exist_ok=True)
    with fitz.open(source) as doc:
        for i, page in enumerate(doc, 1):
            text = page.get_text(sort=True).strip()
            if len(text) < 30:
                blank.append(i)
            page.get_pixmap(dpi=140).save(str(out / "pages" / f"page_{i:03d}.png"))
            sections.append(f"<!-- PDF page {i}: verify columns, equations and tables against pages/page_{i:03d}.png -->\n\n{text}")
    write(out / "paper.pdf.md", "\n\n".join(sections) + "\n")
    save_json(out / "extraction.json", {"method": "pdf-text-with-page-images", "pages": len(sections),
              "low_text_pages": blank, "issues": ["PDF text order/math need visual verification; page images preserve originals"]})
    print(f"Extracted {len(sections)} pages; low-text pages: {blank}")


def crop(args):
    import pymupdf as fitz
    with fitz.open(args.pdf) as doc:
        if not 1 <= args.page <= len(doc):
            raise ValueError("Page number out of range")
        page = doc[args.page - 1]
        rect = fitz.Rect(args.rect) if args.rect else page.rect
        if rect.is_empty or not page.rect.contains(rect):
            raise ValueError("Crop rectangle must be inside the page")
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        page.get_pixmap(dpi=200, clip=rect).save(args.out)


def blocks(text):
    """Split at blank lines outside HTML tables, display math and fenced code."""
    result, buf, table_depth, math_open, fence = [], [], 0, False, None
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if marker:
            if fence is None:
                fence = marker[1][0]
            elif marker[1][0] == fence:
                fence = None
        if fence is None:
            table_depth += len(re.findall(r"<table\b", line, re.I)) - len(re.findall(r"</table\s*>", line, re.I))
            if len(re.findall(r"(?<!\\)\$\$|\\\[|\\\]", line)) % 2:
                math_open = not math_open
        if not stripped and table_depth <= 0 and not math_open and fence is None:
            if buf:
                result.append("".join(buf).strip())
                buf = []
        else:
            buf.append(line)
    if buf:
        result.append("".join(buf).strip())
    if table_depth != 0 or math_open or fence:
        raise ValueError("Unclosed HTML table, display equation or code fence; fix source first")
    return result


def chunk(args):
    source = Path(args.source).resolve()
    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError("Chunk directory is not empty; preserve existing translations")
    text = read(source)
    groups, buf = [], ""
    for block in blocks(text):
        if buf and len(buf) + len(block) > args.size:
            groups.append(buf)
            buf = ""
        buf += ("\n\n" if buf else "") + block
    if buf:
        groups.append(buf)
    entries = []
    for i, group in enumerate(groups, 1):
        name = f"chunk_{i:03d}.md"
        value = group + "\n"
        write(out / name, value)
        entries.append({"file": name, "sha256": sha(value), "chars": len(value)})
    save_json(out / "manifest.json", {"source": str(source.relative_to(out.parent)), "sha256": sha(text), "chunks": entries})
    print(f"Created {len(entries)} chunks")


IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^\n]+?)\)")
MATH_RE = re.compile(r"(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<![\\$])\$(?!\$)(?:\\.|[^$\n])*?(?<!\\)\$")
NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_])[-+−]?\d+(?:[.,]\d+)*(?:[%％])?")


def signature(text):
    doc = soup(text)
    tables = []
    for table in doc.find_all("table"):
        if table.find_parent("table"):
            continue
        tables.append([(tag.name, tag.get("colspan"), tag.get("rowspan")) for tag in table.find_all(["table", "tr", "td", "th"])])
    math = [re.sub(r"\s+", "", html.unescape(m[0])) for m in MATH_RE.finditer(text)]
    without_math = MATH_RE.sub("", text)
    without_math = IMAGE_RE.sub("", without_math)
    without_math = re.sub(r"<[^>]*>", " ", without_math)
    # Keep decimal/scientific values, but ignore section/list numbering prefixes.
    without_math = re.sub(r"(?m)^\s*(?:#{1,6}\s+)?\d+(?:\.\d+)*[.)]?\s+", "", without_math)
    markdown_tables = []
    for block in blocks(text):
        lines = block.splitlines()
        if len(lines) > 1 and re.match(r"^\s*\|?\s*:?-{3,}", lines[1]) and "|" in lines[1]:
            markdown_tables.append([len(re.split(r"(?<!\\)\|", line.strip().strip("|"))) for line in lines])
    return {"images": IMAGE_RE.findall(text), "math": math, "tables": tables, "markdown_tables": markdown_tables,
            "numbers": Counter(NUMBER_RE.findall(without_math)),
            "list_items": len(re.findall(r"(?m)^\s*(?:[-*+] |\d+[.)] )", text)),
            "footnotes": Counter(re.findall(r"\[\^([^\]]+)\]", text))}


def compare(source, translated):
    a, b = signature(source), signature(translated)
    return [key for key in a if a[key] != b[key]]


def assembled(paper):
    folder = paper / "chunks_zh"
    manifest = json.loads(read(folder / "manifest.json"))
    source = read(folder.parent / manifest["source"])
    if sha(source) != manifest["sha256"]:
        raise ValueError("Main source changed after chunking")
    originals, translated = [], []
    for item in manifest["chunks"]:
        original = read(folder / item["file"])
        if sha(original) != item["sha256"]:
            raise ValueError(f"Source chunk modified: {item['file']}")
        target = folder / item["file"].replace(".md", ".zh.md")
        value = read(target)
        if not value.strip():
            raise ValueError(f"Empty translation: {target.name}")
        differences = compare(original, value)
        if differences:
            raise ValueError(f"{target.name}: mismatched {', '.join(differences)}")
        originals.append(original.strip())
        translated.append(value.strip())
    # Detect missing/reordered source chunks even if someone edits the manifest.
    if "\n\n".join(originals) != "\n\n".join(blocks(source)):
        raise ValueError("Source chunks do not cover the full main text in order")
    return "\n\n".join(translated) + "\n"


def render(source):
    import markdown
    source = Path(source)
    text = read(source)
    protected = []

    def protect(match):
        protected.append(html.unescape(match[0]))
        return f"PAPERMATHTOKEN{len(protected)-1}END"

    body = markdown.markdown(MATH_RE.sub(protect, text), extensions=["tables", "fenced_code", "footnotes", "sane_lists"])
    for i, value in enumerate(protected):
        body = body.replace(f"PAPERMATHTOKEN{i}END", html.escape(value, quote=False))
    doc = soup(body)
    for tag in doc.find_all("img"):
        src = tag.get("src", "")
        if src.startswith("data:"):
            continue
        asset = local_asset(source.parent, src)
        payload = asset.read_bytes()
        mime = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
        tag["src"] = "data:" + mime + ";base64," + base64.b64encode(payload).decode()
    title = re.search(r"(?m)^#\s+(.+)", text)
    title = html.escape(title[1] if title else source.stem)
    page = '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>''' + title + '''</title>
<style>
:root{color-scheme:light}body{font-family:"Noto Serif CJK SC","Source Han Serif SC","Songti SC","SimSun",serif;max-width:860px;margin:40px auto;padding:0 24px;line-height:1.8;color:#222;font-size:16px;overflow-wrap:break-word}
h1{font-size:1.7em;border-bottom:2px solid #444;padding-bottom:8px}h2{font-size:1.35em;margin-top:1.8em;border-bottom:1px solid #ccc}h3{font-size:1.15em}
table{display:block;overflow-x:auto;border-collapse:collapse;margin:16px 0;font-size:14px}th,td{border:1px solid #aaa;padding:6px 10px;text-align:center}th{background:#f3f4f6}
img{max-width:100%;height:auto;display:block;margin:16px auto}blockquote{border-left:4px solid #bbb;padding-left:14px;color:#555}pre{padding:14px;overflow:auto;background:#f5f5f5}code{background:#f5f5f5}mjx-container[display="true"]{overflow-x:auto;overflow-y:hidden;padding:8px 0}
.notice{font-family:system-ui,sans-serif;font-size:12px;color:#666;border-bottom:1px solid #ddd;padding-bottom:8px}@media print{body{margin:0;max-width:none}.notice{display:none}}
</style>
<script>window.MathJax={tex:{inlineMath:[['$','$'],['\\\\(','\\\\)']],displayMath:[['$$','$$'],['\\\\[','\\\\]']]}};</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
</head><body><p class="notice">图片已内嵌；公式排版需联网加载 MathJax。未加载时保留 LaTeX 原式。</p>
''' + str(doc) + "\n</body></html>\n"
    target = source.with_suffix(".html")
    write(target, page)
    return target


def assemble(args):
    paper = Path(args.paper)
    validate_name(args.name)
    value = assembled(paper)
    for src in IMAGE_RE.findall(value):
        if not local_asset(paper, src).is_file():
            raise ValueError(f"Missing image: {src}")
    target = paper / f"{args.name}.zh.md"
    write(target, value)
    print(render(target))


def validate_name(name):
    if not name or re.search(r'[<>:"/\\|?*]', name) or name.endswith((" ", ".")) or name.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}:
        raise ValueError("Invalid portable file name")


def check(args):
    paper = Path(args.paper)
    validate_name(args.name)
    errors = []
    required = ["source.pdf", "notes.md", "reading_card.md", "status.json", "main.en.md",
                "glossary.md", f"{args.name}.zh.md", f"{args.name}.zh.html"]
    for name in required:
        if not (paper / name).is_file() or (paper / name).stat().st_size == 0:
            errors.append(f"Missing or empty: {name}")
    try:
        value = assembled(paper)
        if value != read(paper / f"{args.name}.zh.md"):
            errors.append("Final Markdown differs from translated chunks")
        for src in IMAGE_RE.findall(value):
            if not local_asset(paper, src).is_file():
                errors.append(f"Missing image: {src}")
        for tag in soup(read(paper / f"{args.name}.zh.html")).find_all("img"):
            if not tag.get("src", "").startswith("data:"):
                errors.append("Preview contains a non-embedded image")
        status = json.loads(read(paper / "status.json"))
        for key in ["title", "source_url", "version", "scope", "stage", "completed_chunks", "remaining", "issues"]:
            if key not in status:
                errors.append(f"Missing status field: {key}")
        if status.get("remaining") or status.get("issues"):
            errors.append("Status records unfinished items or unresolved issues")
        footnotes = re.findall(r"\[\^([^\]]+)\](?!:)", value)
        definitions = re.findall(r"(?m)^\[\^([^\]]+)\]:", value)
        if set(footnotes) != set(definitions) or len(definitions) != len(set(definitions)):
            errors.append("Footnote references/definitions do not match")
    except Exception as exc:
        errors.append(str(exc))
    report = {"structure_passed": not errors, "errors": errors, "semantic_review": "Agent must review full text and original object inventory"}
    save_json(paper / "validation.json", report)
    print(json.dumps(report, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("extract-html")
    p.add_argument("--url")
    p.add_argument("--file")
    p.add_argument("--out", required=True)
    p.set_defaults(func=extract_html)
    p = sub.add_parser("extract-pdf")
    p.add_argument("--pdf", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=extract_pdf)
    p = sub.add_parser("crop")
    p.add_argument("--pdf", required=True)
    p.add_argument("--page", type=int, required=True)
    p.add_argument("--rect", nargs=4, type=float)
    p.add_argument("--out", required=True)
    p.set_defaults(func=crop)
    p = sub.add_parser("chunk")
    p.add_argument("--source", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--size", type=int, default=7000)
    p.set_defaults(func=chunk)
    for name, func in [("assemble", assemble), ("check", check)]:
        p = sub.add_parser(name)
        p.add_argument("--paper", required=True)
        p.add_argument("--name", required=True)
        p.set_defaults(func=func)
    p = sub.add_parser("render")
    p.add_argument("--source", required=True)
    p.set_defaults(func=lambda args: print(render(args.source)))
    args = parser.parse_args()
    if args.command == "extract-html" and not (args.file or args.url):
        parser.error("extract-html requires --file or --url")
    try:
        args.func(args)
    except (ValueError, OSError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
