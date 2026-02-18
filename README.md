# Custom Equation Tags

A [Quarto](https://quarto.org/) filter extension that lets you assign custom text tags to display math equations instead of automatic numbering, while preserving cross-reference support.

## Usage

Install the extension:

```bash
quarto add alexander-newton/custom-equation-tags
```

Then add the filter to your document header:

```yaml
filters:
  - custom-equation-tags
```

### Tagged equations

Add a `tag` attribute to any display equation to replace its number with a custom label:

```markdown
$$Y \uparrow^{t} E \mid S \setminus \{ Y \}$${#eq-upstream tag="Condition"}
```

This renders the equation with "Condition" as its tag instead of a sequential number.

### Cross-references

Reference tagged equations with the standard `@eq-` syntax:

```markdown
See @eq-upstream for details.
```

This produces a link displaying the custom tag text (e.g. "Condition") rather than "Equation 1".

### Mixing tagged and numbered equations

Normal equations continue to be numbered sequentially, skipping any tagged equations:

```markdown
$$x = y + z$${#eq-first}

$$a = b$${#eq-tagged tag="My Tag"}

$$c = d + e$${#eq-second}
```

Here `eq-first` is "Equation 1", `eq-tagged` displays "My Tag", and `eq-second` is "Equation 2".

## Output formats

Supports HTML and PDF (LaTeX) output.

## Verification

A test document (`test.md`) and verification script (`verify.py`) are included. To run:

```bash
quarto render test.md --to html
uv run verify.py
```
