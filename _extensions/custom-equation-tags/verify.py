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
