"""Rebuild the frozen Danish Fraktur pilot from attributed source snapshots."""

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from unicodedata import normalize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_OUTPUT = ROOT / ".cache" / "danish-fraktur-v1"
VERSION = "1.0.0-draft"


def expand_template(match: re.Match) -> str:
    name, *args = match[1].split("|")
    name = name.strip().lower()
    if name.startswith("#expr:"):
        expression = re.fullmatch(r"#expr:(\d+) mod 2", name)
        if expression:
            return str(int(expression[1]) % 2)
    if name.startswith("#ifeq:") and len(args) == 2:
        return args[1] if name[6:] == args[0] else ""
    if name in {"streg", "afstand", "nop"}:
        return ""
    if name in {"sp", "small", "centrer", "højre"} and len(args) == 1:
        return args[0]
    if name == "hoved" and len(args) == 3:
        return " ".join(args)
    if name == "venstremargen" and len(args) == 2:
        return args[1]
    if name == "bindestreg1" and len(args) == 1:
        return args[0] + "-"
    if name == "bindestreg2" and len(args) == 2:
        return args[0]  # Only the fragment printed on THIS page.
    raise ValueError(f"Unsupported template: {match[0]}")


def plain_text(wikitext: str) -> str:
    if 'pagequality level="4"' not in wikitext:
        raise ValueError("Only validated source revisions are accepted")
    if re.search(r"<ref(?:\s|>)", wikitext):
        raise ValueError("Footnotes require separate alignment; excluded from this pilot")
    text = wikitext
    while "{{" in text:
        expanded = re.sub(r"\{\{([^{}]+)\}\}", expand_template, text)
        if expanded == text:
            raise ValueError("Unresolved template")
        text = expanded
    text = re.sub(r"</?(?:noinclude|h[1-6]|poem)\b[^>]*>", "\n", text)
    text = re.sub(r"</?(?:i|b)>", "", text)
    text = re.sub(r"<(?:pagequality|references)\b[^>]*/>", "", text)
    text = re.sub(r"'{2,5}", "", text)
    if re.search(r"[<>]|\[\[|\]\]|\{\{|\}\}", text):
        raise ValueError("Unresolved wiki markup")
    return normalize("NFC", " ".join(html.unescape(text).split()))


def build_records() -> list[dict]:
    sources = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    review = json.loads((HERE / "review.json").read_text(encoding="utf-8"))
    if len({row["id"] for row in sources}) != len(sources):
        raise ValueError("Duplicate sample IDs")
    if set(review["pages"]) != {row["id"] for row in sources}:
        raise ValueError("Every selected page must have a review record")
    records = []
    for source in sources:
        source = dict(source)
        raw = source.pop("source_wikitext")
        if hashlib.sha256(raw.encode()).hexdigest() != source["source_wikitext_sha256"]:
            raise ValueError(f"Changed source snapshot: {source['id']}")
        text = plain_text(raw)
        corrections = review["pages"][source["id"]]
        for old, new in corrections.get("replacements", []):
            if text.count(old) != 1:
                raise ValueError(f"Ambiguous correction in {source['id']}: {old!r}")
            text = text.replace(old, new, 1)
        if corrections.get("append"):
            text += "\n" + corrections["append"]
        if not text.strip():
            raise ValueError(f"Empty reference: {source['id']}")
        records.append({
            **source, "dataset_version": VERSION, "split": "test", "language": "da",
            "script": "Fraktur", "task": "page-transcription",
            "image_path": f"images/{source['id']}.jpg", "text": text,
            "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "review_method": review["method"], "review_date": review["date"],
        })
    return records


def write_review(records: list[dict], output: Path) -> None:
    sections = []
    for row in records:
        title = html.escape(f"{row['book_title']} — scan page {row['scan_page']}")
        sections.append(
            f'<section id="{row["id"]}"><h2>{title}</h2><p>'
            f'<a href="{html.escape(row["source_revision_url"])}">Pinned transcription</a> · '
            f'<a href="{html.escape(row["source_history_url"])}">Contributors</a></p>'
            f'<div class="pair"><a href="{row["image_path"]}">'
            f'<img loading="lazy" src="{row["image_path"]}" alt="{title}"></a>'
            f'<pre>{html.escape(row["text"])}</pre></div></section>'
        )
    (output / "review.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Danish Fraktur — review</title><style>'
        'body{font:16px system-ui;margin:24px auto;max-width:1500px;padding:0 24px;color:#222}'
        'a{color:#ac1729}section{border-top:1px solid #ddd;margin-top:36px;padding-top:16px}'
        '.pair{display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:start}'
        'img{width:100%}pre{white-space:pre-wrap;font:18px/1.7 Georgia,serif;margin:0}'
        '@media(max-width:800px){.pair{grid-template-columns:1fr}}</style>'
        '<h1>Danish Fraktur — 20-page pilot</h1>'
        '<p>Draft, version ' + VERSION + '. Scans: public domain. Transcriptions: '
        '<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>, '
        'Danish Wikisource contributors, with ScandiOCR corrections. '
        'Click any scan for its full image.</p>' + "".join(sections) + '</html>\n',
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write-manifest", action="store_true", help="Update the checked-in manifest after reviewing source/correction changes")
    args = parser.parse_args()
    records = build_records()
    content = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records)
    manifest = HERE / "manifest.jsonl"
    if args.write_manifest:
        manifest.write_text(content, encoding="utf-8")
    elif not manifest.exists() or manifest.read_text(encoding="utf-8") != content:
        raise ValueError("Rebuilt data differs from the frozen manifest; review before using --write-manifest")

    # Use the same hash-checked download path as evaluation.
    import sys
    sys.path.insert(0, str(ROOT))
    from ocr_datasets.datasets.danish_fraktur import download_image

    args.output.mkdir(parents=True, exist_ok=True)
    for row in records:
        download_image(row, args.output)
    (args.output / "test.jsonl").write_text(content, encoding="utf-8")
    for filename in ("README.md", "LICENSE.txt", "review.json", "sources.json"):
        (args.output / filename).write_bytes((HERE / filename).read_bytes())
    write_review(records, args.output)
    print(f"Prepared {len(records)} pages in {args.output.resolve()}")
    print(f"Review: {(args.output / 'review.html').resolve()}")


if __name__ == "__main__":
    main()
