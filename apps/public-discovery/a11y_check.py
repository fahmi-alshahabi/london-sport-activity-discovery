"""Static accessibility checker (a SUBSET of WCAG 2.2 AA, automated).

AI-ASSISTED SCAFFOLD. This is ONE input, not conformance (WP §11.1): contrast, screen-reader
output and focus behaviour are manual and reviewed by a non-author (C-BLOCK-03). It parses rendered
HTML (stdlib only) and flags structural failures that are cheap to catch automatically.
"""
from __future__ import annotations
from html.parser import HTMLParser


class _A11yParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.html_lang = None
        self.title_text = ""
        self._in_title = False
        self.h1_count = 0
        self.ids = set()
        self.label_for = set()
        self.controls = []          # (tag, attrs-dict)
        self.issues = []
        self.imgs = []
        self._stack = []            # (tag, attrs-dict, text-accumulator)
        self.interactive_text = []  # (tag, attrs-dict, text)

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = a.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self.h1_count += 1
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "label" and a.get("for"):
            self.label_for.add(a["for"])
        if tag in ("input", "select", "textarea"):
            self.controls.append((tag, a))
        if tag == "img":
            self.imgs.append(a)
        if "tabindex" in a:
            try:
                if int(a["tabindex"]) > 0:
                    self.issues.append(f"positive tabindex on <{tag}> (breaks focus order, 2.4.3)")
            except ValueError:
                pass
        if tag in ("a", "button"):
            self._stack.append([tag, a, ""])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in ("a", "button") and self._stack:
            t, a, text = self._stack.pop()
            self.interactive_text.append((t, a, text.strip()))

    def handle_data(self, data):
        if self._in_title:
            self.title_text += data
        if self._stack:
            self._stack[-1][2] += data


def check_html(html: str):
    p = _A11yParser()
    p.feed(html)
    issues = list(p.issues)

    if not p.html_lang:
        issues.append("missing <html lang> (3.1.1)")
    if not p.title_text.strip():
        issues.append("empty or missing <title> (2.4.2)")
    if p.h1_count != 1:
        issues.append(f"expected exactly one <h1>, found {p.h1_count} (1.3.1/2.4.6)")
    if "main" not in p.ids:
        issues.append("no element with id='main' for the skip target (2.4.1)")

    # skip link to #main
    if not any(t == "a" and a.get("href") == "#main" for t, a, _ in p.interactive_text):
        issues.append("missing skip link to #main (2.4.1)")
    # consistent help present (3.2.6)
    if not any(t == "a" and ((a.get("href") or "") == "/help" or (a.get("href") or "").startswith("/help?"))
               for t, a, _ in p.interactive_text):
        issues.append("missing consistent help link to /help (3.2.6)")

    # form controls have a name
    for tag, a in p.controls:
        typ = a.get("type", "")
        if tag == "input" and typ in ("hidden", "submit", "button", "reset"):
            continue
        has_label = a.get("id") in p.label_for
        if not (has_label or a.get("aria-label") or a.get("aria-labelledby") or a.get("title")):
            issues.append(f"<{tag}{(' type='+typ) if typ else ''}> has no associated label (1.3.1/4.1.2)")

    # images need alt
    for a in p.imgs:
        if "alt" not in a:
            issues.append("<img> without alt attribute (1.1.1)")

    # links/buttons need an accessible name
    for t, a, text in p.interactive_text:
        if not text and not a.get("aria-label") and not a.get("aria-labelledby") and not a.get("title"):
            issues.append(f"<{t}> without accessible name (2.4.4/4.1.2)")

    # any <script> should not carry core logic inline (no-JS core, ADR-0001)
    return issues


if __name__ == "__main__":
    import sys
    data = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    problems = check_html(data)
    if problems:
        print("A11Y ISSUES:")
        for i in problems:
            print("  -", i)
        sys.exit(1)
    print("a11y (static subset) OK")
