# Connected collection and page processing

This change connects the existing read-only public-source collector to bounded local PDF extraction/OCR and partition planning. Updating this workflow triggers one run; subsequent runs remain manual. There is no schedule, paid API, LFS, subscription purchase, billing change, automatic repository creation or cross-repository credential setup. Standard ubuntu-latest runners and free Poppler/Tesseract executables are used. Account billing limits are not inspected or modified by this implementation.

## Per-run bounds
The source collector retains its 120-request cap, original-object budget and approved two-host allowlist. Processing attempts at most two incomplete PDF objects and four missing pages per object per run, with an eight-minute soft processing budget and per-command timeouts. Native text is extracted per page. Sparse pages are rendered at 100 DPI and passed to English Tesseract. Temporary page images are removed; source originals remain unchanged. Page text exceeding 2,000,000 UTF-8 bytes or rendered images exceeding 20,000,000 bytes produce explicit failures.

## Resumption and provenance
PDFs are selected only from captured application/pdf ledger entries and deduplicated by source SHA-256. Original bytes are hash-verified. Each derived page records original hash, source URL, page number, extraction method and quality_verified=false. Existing page outputs are skipped, allowing incomplete PDFs to advance on later runs. A document coverage file records the verified expected page count and extracted-page count. Page extraction completeness is not proof of OCR accuracy. Image-only pages may remain empty and unverified.

## Measured partition plan
After processing, the adapter proposes 350,000,000-byte partitions of the original-object directory with per-file hashes. It does not upload or create partitions, include all derived outputs in its size calculation, or solve accumulated Git history growth. Creating or publishing another repository remains a separately approved action. At the last checked checkpoint, original objects occupied 18,974,973 bytes, below the initial partition threshold; this is a historical measurement, not a guaranteed current total.

## Observable results
Read status.json for source acquisition and derived-status.json plus derived/<source-hash>/coverage.json for page processing. proposals/partition-plan.json contains measured proposals only. The workflow attempts to commit available completed outputs even if collection or processing fails, and then marks unsuccessful stages as failed. Runner cancellation or infrastructure failure can still prevent checkpoint publication. A successful workflow does not establish historical completeness or verified transcription accuracy.

## Checks before this commit
Python syntax compilation, captured-PDF deduplication, exclusion of failed ledger records and missing-ledger handling passed local fixture checks. Live OCR and GitHub Actions execution have not been verified before deployment. ArcaSearch, GIS and Legistar live jobs, external vendor ingestion, streaming media and cross-repository publication remain outside this workflow.
