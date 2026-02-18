---
title: "Custom Equation Tags Test"
format:
  html: default
  pdf: default
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

Another normal numbered equation (should be number 2, not 3):

$$a = b + c$${#eq-second}

## Cross-references

- Normal ref: @eq-normal should show "Equation 1"
- Tagged ref: @eq-upstream should show "Condition"
- Tagged ref: @eq-markov should show "Markov"
- Normal ref: @eq-second should show "Equation 2"
