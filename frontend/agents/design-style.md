# Design Style Guide

## 1. Core Principle

Create intentional, distinctive, production-quality interfaces. Avoid generic AI-generated aesthetics, predictable layouts, decorative clutter, and interchangeable SaaS templates.

**Design first. Code second.**

Every page must have a clear visual concept, deliberate composition, meaningful hierarchy, and a reason for its design decisions. Do not start coding immediately by assembling familiar UI patterns.

The goal is not to make every page extravagant. The goal is to make every page feel designed specifically for its purpose.

## 2. Anti-Slop Rules

Never default to the following patterns without a clear, project-specific reason.

### Layout
- Centered headline, subtitle, and two CTA buttons followed by a row of three feature cards.
- Repeated grids of identical rounded cards for every section.
- The same centered container and identical section structure across the entire page.
- Excessive empty space that does not contribute to composition.
- Every element centered regardless of content, hierarchy, or context.
- Predictable hero → features → testimonials → pricing → FAQ layouts copied from SaaS templates.
- Unnecessary wrappers, panels, and nested containers around simple content.

### Visual Styling
- Purple-blue-pink gradients used as a substitute for visual identity.
- Glassmorphism, backdrop blur, glowing borders, and neon accents without a coherent art direction.
- Excessive rounded corners on every element.
- Shadows, borders, and background surfaces applied to everything indiscriminately.
- Decorative blobs, floating circles, random particles, and abstract shapes without a conceptual purpose.
- Emoji used as a replacement for professional icons or custom visual assets.
- Random accent colors, inconsistent radii, and arbitrary spacing values.
- Artificially futuristic styling simply because the interface is a technology product.

### Typography
- Using one font, weight, and scale for almost every text element.
- Oversized headlines that consume the entire viewport without communicating anything meaningful.
- Excessive uppercase labels, tiny tracking-heavy captions, and meaningless eyebrow text.
- Generic headings such as "The Future of...", "Unlock Your Potential", or "Everything You Need" when they do not fit the product.
- Using typography only for readability instead of treating it as a major compositional element.

### Components
- Turning every piece of content into a card.
- Using identical button styles and sizes regardless of importance.
- Adding badges such as "NEW", "AI POWERED", and "BEST CHOICE" purely for decoration.
- Adding icons to every heading, list item, or button without improving comprehension.
- Using default-looking forms, navigation bars, dashboards, and modals without considering the overall visual language.
- Building elaborate UI components that add complexity but no meaningful value.

### Animation
- Animating every element simply because animation is available.
- Applying the same fade-up entrance animation to every section.
- Unnecessary parallax, floating elements, cursor effects, and perpetual motion.
- Motion that delays interaction, harms readability, or distracts from the primary task.
- Using animation to disguise a weak static composition.

These are warning signs, not unconditional bans. A pattern is acceptable when it serves a clear purpose and fits the established design direction.

## 3. Establish a Visual Concept Before Coding

Before implementing a page, determine:

1. **Purpose:** What is the primary user task?
2. **Character:** What should the interface feel like? Choose a specific, coherent direction rather than "modern and clean."
3. **Visual anchor:** What makes this interface recognizable? Examples include distinctive typography, an editorial composition, custom illustrations, a strong product visualization, unusual geometry, or a characteristic motion system.
4. **Hierarchy:** What should users notice first, second, and third?
5. **Composition:** How are content, imagery, negative space, and visual weight distributed?
6. **Interaction:** Which elements respond to user input, and why?
7. **Constraints:** What must remain accessible, responsive, fast, and usable?

Make these decisions before choosing individual components.

Do not write a lengthy design proposal for every small change. For a minor component, infer the established visual language and implement consistently.

## 4. Layout and Composition

Treat the page as a composition, not a stack of sections.

- Establish a clear primary focal point.
- Vary alignment, scale, density, and spatial relationships according to content.
- Use asymmetry, overlapping elements, split layouts, full-bleed sections, or editorial arrangements when appropriate.
- Use negative space intentionally; empty space should create hierarchy, separation, or emphasis.
- Introduce meaningful contrast between sections rather than repeating the same background and container.
- Let important content determine the layout, not the limitations of a default component library.
- Use grids as structural tools, not as a requirement to make everything symmetrical.
- Avoid forcing every section into the same max-width container when a different width would improve the composition.

A distinctive layout does not require chaos. Maintain alignment, rhythm, balance, and clear reading order.

## 5. Typography

Treat typography as a primary design tool.

- Select typefaces that support the product's character and language.
- Establish a deliberate hierarchy for display headings, section headings, body text, labels, and metadata.
- Use meaningful differences in scale, weight, line height, and measure.
- Control headline line breaks and text width to improve both composition and readability.
- Use large display typography only when it supports the message and available space.
- Avoid long lines of body text and excessively small secondary text.
- Use font weights and letter spacing intentionally rather than styling everything as bold.
- Prefer a small, coherent type system over arbitrary values scattered across components.

Do not choose typography solely because a particular font is popular in AI-generated websites.

## 6. Color and Surface Design

Define a coherent color system before styling individual components.

- Choose colors based on the product, brand, content, and desired visual character.
- Establish primary, secondary, background, surface, text, border, and semantic colors where needed.
- Use accent colors to direct attention, not to decorate every element.
- Preserve sufficient contrast and clear interaction states.
- Distinguish surfaces through a deliberate combination of color, spacing, typography, and borders.
- Use gradients, transparency, blur, texture, and shadows only when they strengthen the visual concept.
- Avoid introducing a new color for every component.
- Maintain consistency across pages without making every page visually identical.

A restrained palette is not automatically good design. A colorful palette is not automatically bad design. Both require deliberate control.

## 7. Visual Assets and Distinctiveness

Prefer visual elements that communicate something specific about the product.

When appropriate, use:
- Custom illustrations and diagrams.
- Product screenshots and realistic product visualizations.
- 3D objects and interactive scenes.
- Editorial photography and art-directed imagery.
- Purpose-built backgrounds, textures, and graphic systems.
- Data visualizations that reveal meaningful information.
- Custom icons or distinctive visual motifs.

Do not add graphics merely to fill empty space.

Do not use generic stock imagery, arbitrary 3D objects, or decorative SVG shapes as substitutes for a real concept.

If a page would benefit from a custom visual asset, identify that need explicitly rather than compensating with more cards, gradients, or shadows.

## 8. Motion and Interaction

Motion must have a defined purpose.

Use animation to:
- Explain relationships or state transitions.
- Provide feedback for user actions.
- Establish visual hierarchy.
- Reveal information progressively.
- Make direct manipulation feel natural.
- Support a distinctive visual concept.

Prefer a small number of well-designed, coordinated animations over many unrelated effects.

- Use appropriate easing and duration.
- Keep essential content accessible immediately.
- Avoid unnecessary animation on repeated elements.
- Respect reduced-motion preferences.
- Ensure hover effects have usable touch and keyboard equivalents where relevant.
- Avoid expensive continuous effects that compromise performance.

Do not add animation simply to make the interface appear more sophisticated.

## 9. Component and Design-System Discipline

Components should support the design, not dictate it.

- Reuse components when they represent the same interaction or visual role.
- Do not force unrelated content into one generic card or section component.
- Keep spacing, typography, color, radii, and interaction states consistent.
- Use shared design tokens for recurring values.
- Introduce new variants only when there is a genuine design need.
- Preserve a coherent visual language across pages while allowing different layouts to serve different tasks.
- Avoid unnecessary component abstractions that constrain composition.

Consistency means shared design logic, not identical presentation everywhere.

## 10. Responsive Design

Design for different screen sizes rather than merely shrinking the desktop layout.

- Reconsider composition and hierarchy on smaller screens.
- Adapt typography, spacing, alignment, and visual assets to the available space.
- Remove or simplify decorative elements when they interfere with content.
- Preserve the primary interaction and content hierarchy.
- Prevent horizontal overflow and cramped layouts.
- Make navigation, forms, buttons, and interactive elements comfortable to use on touch devices.
- Do not assume that a desktop composition can be reproduced by stacking all elements vertically.

Responsive behavior is part of the original design, not a final patch.

## 11. Accessibility and Performance

Visual quality must not compromise usability.

- Maintain readable text and adequate contrast.
- Provide visible keyboard focus states.
- Use semantic HTML and accessible interaction patterns.
- Preserve meaningful labels and error feedback in forms.
- Avoid conveying essential information through color alone.
- Optimize images, 3D assets, and animation.
- Avoid unnecessary dependencies and expensive effects.
- Respect `prefers-reduced-motion`.

Do not sacrifice accessibility or performance for a decorative effect.

## 12. Implementation Workflow

For a new page or substantial redesign:

1. Understand the product, audience, content, and primary user task.
2. Inspect the existing project and identify established design conventions.
3. Choose a distinct visual direction suited to the specific page.
4. Establish composition, hierarchy, typography, color, and visual assets.
5. Implement the page using the existing architecture and conventions.
6. Add purposeful interactions and motion.
7. Review the actual rendered interface at desktop and mobile sizes.
8. Identify and correct generic patterns, visual inconsistencies, and implementation defects.

For an existing project, do not redesign everything unnecessarily. Preserve established decisions unless there is a clear reason to change them.

Do not introduce unrelated architectural refactors while implementing a visual task.

## 13. Final Visual Quality Check

Before considering a page complete, evaluate it against these questions:

- Does the page have a recognizable visual concept?
- Could this exact interface belong to hundreds of unrelated products? If yes, what makes it specific to this product?
- Is there a clear focal point and a deliberate hierarchy?
- Does the layout have meaningful variation rather than repetitive sections?
- Is every card, border, shadow, gradient, icon, and animation justified?
- Does typography contribute to the composition?
- Are the most important interactions immediately understandable?
- Does the page remain coherent on mobile?
- Are accessibility and performance acceptable?
- Does the rendered result match the intended design?

**If the result looks generic, do not fix it by adding more decoration. Reconsider the concept, composition, hierarchy, or visual assets.**

A page is not finished merely because the code compiles, the components render, or the layout follows common conventions.

## 14. Decision Rule

When choosing between a generic, predictable solution and a more distinctive solution:

Prefer the distinctive solution when it improves the product's identity, usability, or visual communication without introducing unnecessary complexity.

When choosing between originality and clarity, preserve clarity.

When choosing between decoration and purpose, preserve purpose.

When choosing between a fashionable effect and a coherent design system, preserve the design system.

The final interface should feel intentional, product-specific, visually coherent, and professionally executed—not like a default template generated from a prompt.