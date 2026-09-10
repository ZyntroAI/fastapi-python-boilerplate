Here are a few workflow patterns for an agent whose job is generating SVGs, depending on what's driving the output:

**1. Data-to-chart pipeline**
1. Validate/parse input data (shape, ranges, missing values)
2. Choose chart type based on data shape (categorical → bar, time series → line, part-whole → pie/donut)
3. Compute layout (viewBox, scales, padding) before drawing elements
4. Generate SVG primitives (axes → gridlines → data → labels/legend last, so they're not obscured)
5. Validate output (well-formed XML, viewBox matches content bounds)

**2. Diagram/flowchart from description**
1. Parse the description into nodes + edges (a simple graph structure) before touching SVG
2. Auto-layout (grid, hierarchical, or force-directed depending on complexity)
3. Draw edges first, then nodes on top (avoids lines cutting through boxes)
4. Add text last, sized to fit its container
5. Check for overlaps/collisions; re-layout if any

**3. Icon/illustration generation**
1. Define a fixed canvas size and grid (e.g., 24×24, 100×100) up front for consistency
2. Sketch structure with simple shapes first (circles/rects/paths as placeholders)
3. Refine paths, add detail
4. Optimize (remove redundant points, consolidate paths)
5. Validate against a style guide if one exists (stroke width, corner radius, color tokens)

**4. Iterative/editable SVG (user refines it conversationally)**
1. Generate a first draft with clearly labeled/grouped `<g>` elements (semantic IDs)
2. On each revision, edit specific groups rather than regenerating the whole file
3. Keep a running "spec" (what each group represents) so edits stay consistent
4. Re-validate viewBox/bounds after each edit, since edits can silently break layout

A cross-cutting rule for all of these: **always use CSS variables for colors** if the SVG needs to adapt to themes, and **compute the viewBox from actual content bounds** rather than guessing — that's the most common source of clipped or off-center SVGs.

Which of these matches what you're building — is this for the Visualizer-style inline diagrams, or a standalone SVG-generation skill/agent?
