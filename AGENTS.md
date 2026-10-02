# Repository instructions for contributors and coding agents

This file governs **work on the CPC repository**. It does not grant control of another project.
To use CPC on another project, read `skills/cybernetic-project-control/SKILL.md` and that project's own instructions first. Do not copy this file over a user's `AGENTS.md`.

## Scope

Maintain a portable project-management skill and small offline reference utilities, not a new agent runtime. User-facing core documentation is Chinese; identifiers and machine fields are English. Keep the installable skill self-contained. Do not hard-code a user's machine, identity, institution, project path or credentials.

## Implementation and evidence

- Every claimed control mechanism needs a behavior, a limitation and a test reference in `theory/traceability.md`.
- Separate book content, modern interpretation and our design. Do not invent quotations or page numbers.
- Never equate valid JSON, file hashes or passing tests with scientific validity or verified authorization.
- Keep external integrations marked `guidance_only` unless exercised against a recorded host/version.
- Do not turn future plans into shipped claims. Public dev cases are not a held-out benchmark.
- No automatic networking, publishing, credential access or execution of commands embedded in input records.
- Do not alter an evaluation oracle merely to make the implementation pass. Explain every change to a case or rubric.

## Checks

```bash
python -m unittest discover -s tests -v
python tools/check_repository.py
python tools/demo.py
```

Optional package-only checks should also work after copying `skills/cybernetic-project-control/` elsewhere.
No original book PDF or external source-code copies belong in release artifacts.
