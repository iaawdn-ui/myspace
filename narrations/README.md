# Narration manuscript production

## Standard

Each course is to become its own PDF manuscript with module-by-module spoken narration, teaching visuals, practical instruction, assessments, and a course-specific cumulative word-count record. The target is **at least 100,000 spoken words per course**, not a single 100,000-word monologue. No faith-related content is to be included.

For technical topics, each manuscript should identify where accurate diagrams, realistic images, code, mathematical notation, simulations, and laboratory illustrations belong. Visual assets should support the narrated lesson, be captioned or described, and not be used as substitutes for explanation.

## Current progress

- **AI.101 — Introduction to Artificial Intelligence:** Four modules written and typeset as separate PDFs, each with a Markdown source: (1) Foundations; (2) Task Environments and Problem Formulation; (3) Problem Formulation and Search; (4) Knowledge Representation and Reasoning. Visuals include an illustrative realistic engineering-lab image, PEAS task specification, agent/environment and system-boundary diagrams, environment classification, state-space search, and knowledge graphs/rule-inference illustrations. Each module includes narration, practical work, knowledge checks or assessment.
- **AI.101 spoken narration progress:** 10,735 words across the four current manuscripts, measured from narration sections only; target is 100,000+ words. This is in progress and does not claim course completion.
- **Remaining courses:** Not yet drafted as narration manuscripts. They will be built course-by-course so that each receives substantive, technically accurate teaching rather than padding or repeated filler.

## Rebuild

```bash
.venv/bin/python scripts/build_ai101_narration_pdf.py
```
