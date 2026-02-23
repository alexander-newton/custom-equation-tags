# /// script
# requires-python = ">=3.10"
# dependencies = ["beautifulsoup4"]
# ///
"""Verify custom equation tags rendered correctly in HTML output."""
import sys
from pathlib import Path
from bs4 import BeautifulSoup

html_path = Path(__file__).parent / "test.html"
if not html_path.exists():
    print(f"FAIL: {html_path} not found. Run: quarto render test.md --to html")
    sys.exit(1)

soup = BeautifulSoup(html_path.read_text(), "html.parser")
errors = []

# Check tagged equations have correct tags
for eq_id, expected_tag in [("eq-upstream", "Condition"), ("eq-markov", "Markov")]:
    span = soup.find(id=eq_id)
    if not span:
        errors.append(f"FAIL: No element with id='{eq_id}' found")
        continue
    raw = str(span)
    if f"\\tag{{{expected_tag}}}" not in raw:
        errors.append(f"FAIL: '{eq_id}' missing tag '{expected_tag}' in equation display")

# Check LaTeX-symbol-tagged equations render without \text{} wrapping
for eq_id, latex_tag in [
    ("eq-pythag", r"\star"),
    ("eq-cyc-star", r"\star"),
    ("eq-dblstar", r"\star\star"),
    ("eq-dagger", r"\dagger"),
    ("eq-pairwise", r"\star"),
    ("eq-pairwise2", r"\dagger"),
]:
    span = soup.find(id=eq_id)
    if not span:
        errors.append(f"FAIL: No element with id='{eq_id}' found for LaTeX-tagged equation")
        continue
    raw = str(span)
    # Should have \tag{$<latex>$} NOT \tag{\text{<latex>}}
    if rf"\tag{{\text{{{latex_tag}}}}}" in raw:
        errors.append(f"FAIL: '{eq_id}' has \\text{{}} wrapping around LaTeX tag '{latex_tag}'")
    if rf"\tag{{${latex_tag}$}}" not in raw:
        errors.append(f"FAIL: '{eq_id}' missing LaTeX tag '{latex_tag}' in equation display")

# Check cross-references for plain-text tags
for eq_id, expected_text in [("eq-upstream", "Condition"), ("eq-markov", "Markov")]:
    link = soup.find("a", href=f"#{eq_id}")
    if not link:
        errors.append(f"FAIL: No link to '#{eq_id}' found")
        continue
    link_text = link.get_text().strip()
    if link_text != expected_text:
        errors.append(f"FAIL: Link to '{eq_id}' says '{link_text}', expected '{expected_text}'")

# Check LaTeX tag cross-references contain math rendering (not plain text)
for eq_id, latex_tag in [
    ("eq-pythag", r"\star"),
    ("eq-cyc-star", r"\star"),
    ("eq-dblstar", r"\star\star"),
    ("eq-dagger", r"\dagger"),
    ("eq-pairwise", r"\star"),
    ("eq-pairwise2", r"\dagger"),
]:
    link = soup.find("a", href=f"#{eq_id}")
    if not link:
        errors.append(f"FAIL: No link to '#{eq_id}' found for LaTeX-tagged equation")
        continue
    # Link should contain a math span for LaTeX rendering, not raw text
    math_span = link.find("span", class_=lambda c: c and "math" in c)
    if not math_span:
        errors.append(
            f"FAIL: Link to '{eq_id}' should contain math rendering for LaTeX tag, "
            f"got plain text: '{link.get_text().strip()}'"
        )

# Check normal equations still have numbers
for eq_id in ["eq-normal", "eq-second"]:
    link = soup.find("a", href=f"#{eq_id}")
    if not link:
        errors.append(f"FAIL: No link to '#{eq_id}' found for normal equation")
        continue
    link_text = link.get_text().strip()
    if "Equation" not in link_text:
        errors.append(f"FAIL: Normal ref '{eq_id}' says '{link_text}', expected 'Equation N'")

# Check cross-references inside math content resolve correctly
# Find display math elements containing \href (MathJax link syntax)
import re

all_math = soup.find_all("span", class_=lambda c: c and "math" in c)
display_math_texts = []
for m in all_math:
    raw = str(m)
    if "display" in raw.lower() or "DisplayMath" in raw:
        display_math_texts.append(raw)

# Gather all math text content to search for resolved refs
all_math_raw = " ".join(str(m) for m in all_math)

# Plain text tag ref inside math: @eq-upstream -> \href{#eq-upstream}{Condition}
if r"\href{#eq-upstream}{Condition}" not in all_math_raw:
    errors.append(
        "FAIL: @eq-upstream inside math not resolved to \\href{#eq-upstream}{Condition}"
    )

# LaTeX symbol tag ref inside math: @eq-pythag -> \href{#eq-pythag}{$\star$}
if r"\href{#eq-pythag}{$\star$}" not in all_math_raw:
    errors.append(
        "FAIL: @eq-pythag inside math not resolved to \\href{#eq-pythag}{$\\star$}"
    )

# Unresolved @patterns should NOT appear for known tags
for eq_id in ["eq-upstream", "eq-pythag"]:
    # Check that no math element still has the raw @eq-id pattern
    # (only check math elements that originally contained a reference)
    pattern = re.compile(r"@" + re.escape(eq_id) + r"(?![{])")
    for m in all_math:
        raw = str(m)
        if pattern.search(raw) and r"\href{#" + eq_id + "}" not in raw:
            errors.append(
                f"FAIL: Unresolved @{eq_id} found in math content: {raw[:100]}"
            )

# Check numbering: normal equations should be 1 and 2 (no gap)
for eq_id, expected_num in [("eq-normal", "1"), ("eq-second", "2")]:
    span = soup.find(id=eq_id)
    if not span:
        continue
    raw = str(span)
    if f"\\tag{{{expected_num}}}" not in raw:
        errors.append(f"FAIL: '{eq_id}' should be numbered {expected_num}")

if errors:
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print("PASS: All checks passed")
    sys.exit(0)
