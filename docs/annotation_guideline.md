# Gold annotation guideline

1. Read the complete USAspending definition, not only the field name.
2. Compare it against the canonical OCDS property definition and type.
3. Record every semantically valid target in the fixed 108-property subset.
4. Use `1:n` only when the single source value can validly populate multiple
   selected target paths.
5. Use `no-match` when the fixed target has no named equivalent. Do not map to
   generic `details` merely because it could hold arbitrary extension data.
6. Preserve code-versus-label distinctions and date/amount semantics.
7. Cite both the source field and target schema path.
8. Do not change the target after viewing a difficult source mapping.
9. Mark uncertainty as `ambiguous` instead of forcing a target.
10. Independent domain review, if later performed, must update
    `review_status` without rewriting the historical draft hash.

The current file is `draft_complete` and deterministically validated, but not
independently reviewed by a procurement subject-matter expert.

