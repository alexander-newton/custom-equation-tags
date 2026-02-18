-- Custom Equation Tags Quarto Filter
-- Allows $$...$$​{#eq-name tag="Label"} syntax for custom equation labels

-- Store tagged equations for cross-reference resolution
local eq_tags = {}

-- Extract text from a Quoted AST node
-- Quoted node contains the inline content in c[1]
local function extract_quoted_text(quoted_node)
  if quoted_node and quoted_node.t == "Quoted" then
    if quoted_node.c and #quoted_node.c >= 1 then
      local content = quoted_node.c[1]
      return pandoc.utils.stringify(content)
    end
  end
  return nil
end

-- Parse equation attributes from inline elements
-- Returns (eq_id, tag_value, end_index) or nil if not a tagged equation
-- start is the index of the Math element
local function parse_eq_attr(inlines, start)
  local math_elem = inlines[start]
  if not math_elem or math_elem.t ~= "Math" then
    return nil
  end

  -- Look for the attribute block starting at start+1
  local i = start + 1
  if i > #inlines then
    return nil
  end

  local first = inlines[i]

  -- Check if we have {#eq-id pattern
  if first.t ~= "Str" or not string.match(first.text, "^{#") then
    return nil
  end

  -- Extract eq_id from {#eq-id (handles both {#eq-id} and {#eq-id with content after)
  local eq_id = string.match(first.text, "^{#([^%s}]+)")
  if not eq_id then
    return nil
  end

  -- Check if this is a simple closing like {#eq-id} (no tag)
  if string.match(first.text, "^{#[^%s}]+}$") then
    -- Simple untagged equation
    return eq_id, nil, i
  end

  -- Look for tag="..." in following elements
  local tag_value = nil
  i = i + 1
  local found_tag = false

  while i <= #inlines do
    local elem = inlines[i]

    if elem.t == "Str" then
      -- Check for closing brace first (may be {#eq-id} pattern)
      if string.match(elem.text, "^}") then
        -- Found closing brace without tag, return untagged equation
        return eq_id, nil, i
      end
      -- Check for tag= pattern
      if string.match(elem.text, "^tag=") then
        found_tag = true
        i = i + 1
        -- Next element should be the Quoted value
        if i <= #inlines and inlines[i].t == "Quoted" then
          tag_value = extract_quoted_text(inlines[i])
          i = i + 1
          -- After quoted value, look for closing brace
          if i <= #inlines and inlines[i].t == "Str" then
            local closing = inlines[i].text
            if string.match(closing, "^}") then
              return eq_id, tag_value, i
            end
          end
          return nil  -- Malformed
        end
        return nil  -- Malformed
      end
    elseif elem.t == "Space" then
      i = i + 1
    else
      -- Unexpected element, not an attribute block
      return nil
    end
  end

  return nil
end

-- Strip attribute tokens from inlines, returning new inlines list
local function strip_attributes(inlines, start, end_idx)
  local result = {}
  for i = 1, start - 1 do
    table.insert(result, inlines[i])
  end
  for i = end_idx + 1, #inlines do
    table.insert(result, inlines[i])
  end
  return result
end

-- Inject \tag{} into LaTeX math
local function inject_tag(math_content, tag_value)
  -- For display math, we inject the tag command
  return "\\tag{\\text{" .. tag_value .. "}} " .. math_content
end

-- Store math content for LaTeX processing
local eq_math = {}

-- Pass 1: Parse equations and transform them
local function process_para(el)
  local inlines = el.content
  local i = 1

  while i <= #inlines do
    local elem = inlines[i]

    -- Look for Math elements
    if elem.t == "Math" and elem.mathtype == "DisplayMath" then
      local eq_id, tag_value, end_idx = parse_eq_attr(inlines, i)

      if eq_id and tag_value then
        -- This is a tagged equation
        eq_tags[eq_id] = tag_value
        eq_math[eq_id] = elem.text

        -- Strip the attribute tokens
        inlines = strip_attributes(inlines, i, end_idx)

        -- Transform based on format
        if quarto.doc.is_format("html") then
          -- HTML: inject \tag into math and wrap in Span with id
          local new_math = pandoc.Math(
            "DisplayMath",
            inject_tag(elem.text, tag_value)
          )
          local span = pandoc.Span({new_math}, pandoc.Attr(eq_id, {"tagged-equation"}))

          -- Replace the Math element with the Span
          inlines[i] = span
        elseif quarto.doc.is_format("latex") or quarto.doc.is_format("pdf") then
          -- LaTeX: mark for conversion to raw block
          -- Store a marker with the equation ID
          local marker_inline = pandoc.RawInline("latex", "\\begin{equation*}\\tag{" .. tag_value .. "}\\label{" .. eq_id .. "}\n" .. elem.text .. "\n\\end{equation*}")
          inlines[i] = marker_inline
        end
      end
    end

    i = i + 1
  end

  -- For LaTeX, convert the paragraph with equation blocks into proper block structure
  if quarto.doc.is_format("latex") or quarto.doc.is_format("pdf") then
    local new_content = {}
    local blocks = {}

    for i = 1, #inlines do
      local elem = inlines[i]
      if elem.t == "RawInline" and string.match(elem.text or "", "^\\\\begin{equation") then
        -- This is a LaTeX equation block
        if #new_content > 0 then
          table.insert(blocks, pandoc.Para(new_content))
          new_content = {}
        end
        -- Convert RawInline to RawBlock
        local raw_block = pandoc.RawBlock("latex", elem.text)
        table.insert(blocks, raw_block)
      else
        table.insert(new_content, elem)
      end
    end

    -- If we created any blocks, return them instead of a para
    if #blocks > 0 then
      if #new_content > 0 then
        table.insert(blocks, pandoc.Para(new_content))
      end
      return blocks
    end
  end

  el.content = inlines
  return el
end

-- Pass 2: Resolve cross-references
local function resolve_cites(el)
  if el.t == "Cite" then
    -- Check if this is a reference to a tagged equation
    local cite_id = el.citations[1].id
    if cite_id and eq_tags[cite_id] then
      local tag_value = eq_tags[cite_id]

      if quarto.doc.is_format("html") then
        -- HTML: create a link to the equation
        return pandoc.Link(
          {pandoc.Str(tag_value)},
          "#" .. cite_id,
          "",
          {class = "quarto-xref"}
        )
      elseif quarto.doc.is_format("latex") or quarto.doc.is_format("pdf") then
        -- LaTeX: use hyperref
        return pandoc.RawInline(
          "latex",
          "\\hyperref[" .. cite_id .. "]{" .. tag_value .. "}"
        )
      end
    end
  end
  return el
end

-- Return filter structure with two passes
return {
  {
    Para = process_para
  },
  {
    Cite = resolve_cites
  }
}
