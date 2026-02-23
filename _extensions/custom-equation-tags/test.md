---
title: "Custom Equation Tags Test"
format:
  html: default
  pdf:
    keep-tex: true
filters:
  - custom-equation-tags.lua
---

## Test Section

A normal numbered equation:

$$x = y + z$${#eq-normal}

A tagged equation (should show "Condition" not a number):

$$Y \uparrow^{t} E \mid S \setminus \{ Y \}$${#eq-upstream tag="Condition"}

Another tagged equation:

$$E \perp^t \sigma(\mathcal{C}(E) \setminus S) \mid \sigma(S)$${#eq-markov tag="Markov"}

A LaTeX-symbol-tagged equation (should show "★" not "\star"):

$$x^2 + y^2 = z^2$${#eq-pythag tag="\star"}

A dollar-wrapped LaTeX tag (should show "★" same as bare backslash):

$$y = x$${#eq-cyc-star tag="$\star$"}

Dollar-wrapped double-star tag:

$$\frac{a}{b} = \frac{c}{d}$${#eq-dblstar tag="$\star\star$"}

Dollar-wrapped dagger tag:

$$\alpha + \beta = \gamma$${#eq-dagger tag="$\dagger$"}

Inline-paragraph equation with dollar-wrapped tag. For any variables $X_i$ and $X_j$, consider $$\frac{P^{t_{X_j}}(X_i)}{P^{t_{X_i}}(X_j)} = \frac{P^t(X_i)}{P^t(X_j)}.$${#eq-pairwise tag="$\star$"}

Another inline-paragraph equation referencing prior tags. Combined with @eq-pairwise, this means $$\frac{Q(X_i)}{Q(X_j)} = \frac{R(X_i)}{R(X_j)}. $${#eq-pairwise2 tag="$\dagger$"}

Xrefs to @eq-pairwise and @eq-pairwise2 in running text.

Another normal numbered equation (should be number 2, not 3):

$$a = b + c$${#eq-second}

## Cross-references

- Normal ref: @eq-normal should show "Equation 1"
- Tagged ref: @eq-upstream should show "Condition"
- Tagged ref: @eq-markov should show "Markov"
- LaTeX tag ref: @eq-pythag should show the star symbol
- Dollar-wrapped LaTeX tag ref: @eq-cyc-star should show the star symbol
- Double-star tag ref: @eq-dblstar should show ★★
- Dagger tag ref: @eq-dagger should show †
- Inline equation ref: @eq-pairwise should show ★
- Inline equation ref: @eq-pairwise2 should show †
- Normal ref: @eq-second should show "Equation 2"

## Cross-references inside math

A plain-text tag ref inside math (should resolve "Condition" as a link):

$$\text{Truncated Factorization (@eq-upstream)} = 0$$

A LaTeX-symbol tag ref inside math (should resolve star symbol as a link):

$$\text{See @eq-pythag for details}$$

Multiple refs inside one equation:

$$\text{Combining @eq-upstream and @eq-pythag gives a result}$$
