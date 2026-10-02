# Release checklist / 发布清单

This checklist is for **future CPC releases**. The repository itself is already public; a new version should still pass the checks below before it is tagged or announced.

1. Review README, SECURITY, NOTICE, ownership, visibility and license.
2. Scan for private data, credentials, the source book PDF and real project paths. Public examples must remain synthetic.
3. Run:
   ```bash
   python -m unittest discover -s tests -v
   python tools/check_repository.py
   python tools/demo.py
   ```
4. Update `reports/STATUS.md`. Do not turn engineering tests into a live-agent efficacy claim.
5. Verify the standalone Skill package contains every referenced asset/script/reference and no source book.
6. Check bilingual README links, `CITATION.cff`, `codemeta.json`, issue templates and CI.
7. Record exact host/model versions for any integration or efficacy claim.
8. Tag/release only after reviewing the final Git diff.

## Local packaging

From the repository root:

```bash
python tools/package_release.py --output /path/to/fresh-release-directory
```

The output directory must be outside the source repository and must be fresh. The tool creates a source ZIP, a standalone Skill ZIP and SHA-256 manifests. It deliberately excludes caches, local/source directories, real eval runs, private fixtures, PDFs, keys and environment files.

The packager checks byte integrity; it is not a signature, secret scanner, license audit or agent evaluation.

## Publication metadata

Recommended repository description:

> A portable project-control skill for AI agents managing long-running research and engineering projects, grounded in Engineering Cybernetics.

Recommended discoverability topics are documented in the README/search terms and should be configured in GitHub repository settings when the account/API permits.
