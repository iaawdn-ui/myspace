# Narration manuscript production

## Standard

Each course is to become its own PDF manuscript with module-by-module spoken narration, teaching visuals, practical instruction, assessments, and a course-specific cumulative word-count record. The target is **at least 100,000 spoken words per course**, not a single 100,000-word monologue. No faith-related content is to be included.

For technical topics, each manuscript should identify where accurate diagrams, realistic images, code, mathematical notation, simulations, and laboratory illustrations belong. Visual assets should support the narrated lesson, be captioned or described, and not be used as substitutes for explanation.

## Current progress

- **AI.101 — Introduction to Artificial Intelligence:** Module 1, “What Is Artificial Intelligence?”, written and typeset as `AI101_Module_01_Foundations.pdf` with its source manuscript in Markdown. Includes an illustrative realistic lab image, an agent–environment diagram, a task/method/application map, narration, practical exercise, knowledge check, and assignment.
- **Course word-count target:** 100,000+ spoken words. This first module is an installment; it does not claim completion of the course target.
- **Remaining courses:** Not yet drafted as narration manuscripts. They will be built course-by-course so that each receives substantive, technically accurate teaching rather than padding or repeated filler.

## Rebuild

```bash
.venv/bin/python scripts/build_ai101_narration_pdf.py
```
