# Cheyenne and Laramie County public-record archive

## Scope
Preserve actual authorized public-government records, not merely links. Initial seeds cover city meetings and finance and county meetings, finance and mapping. This registry is provisional: the uploaded Wyoming workbook has not been exhaustively imported or reconciled. School districts, other county communities, procurement, planning, utilities, elections and historical vendor archives require additional inventory and source-specific adapters.

## Historical collections
The county Clerk describes historical commissioner minutes from January 1868 through June 1994 and a contemporary system from January 1991 onward. These advertised ranges are not independently verified completeness claims. Historical endpoint: https://gov.arcasearch.com/uswylrc/ . Official description: https://www.laramiecountywy.gov/County-Government/Elected-Officials/County-Clerk/Clerk-to-the-Board-of-County-Commissioners . Overlapping records must retain both representations without double-counting events.

## Acquisition
The first collector follows same-allowlist HTTPS links without a depth cutoff, subject to robots rules and conservative request, time and storage budgets. It preserves original bytes by SHA-256, HTML text and provenance. Pagination with distinct ordinary URLs is followed; JavaScript-only pages, APIs, viewer-specific downloads, video, and external vendor archives are not yet implemented. No login, CAPTCHA or paywall bypass. No private repositories, Drive files, commentary, or research are imported.

## Rights and sensitive information
Only intentionally published, non-sensitive public records should be mirrored. Robots permission is not a copyright license. Do not add restricted, inadvertently exposed, personal-case, juvenile, health, credential, or private-research sources. Uncertain-rights vendor material and GIS feature databases require separate review. The collector only logs external links and does not copy them. Preserve publisher notices. Do not assign a blanket open license to source records.

## Financial and GIS scope
City finance includes budgets, audits, capital plans, narratives, quarterly reports and tax reports. County finance includes budgets and audited statements; online copies do not establish complete invoice coverage. Mapping metadata and HTML are not equivalent to feature-level exports. GIS data exports need an adapter, count reconciliation and rights review.

## Repository partitioning
Initial repository-wide object budget: 400,000,000 bytes. Individual download limit: 20,000,000 bytes. Per-run request cap: 120, with at least two seconds between requests. Oversized objects and exhausted storage are logged as gaps, never silently truncated. At the storage threshold, collection pauses and a new partition must be approved and registered; this implementation does not create repositories or enable billing. Large city budgets, scanned historical volumes and media may exceed the initial per-file limit and remain explicit gaps.

## Completion criteria
A run finishing is not archive completion. Reconcile discovered and captured URLs, attachment sets, dates, body/volume inventories, failures, external candidates, unsupported services and offline holdings. Source text remains distinct from OCR and analysis. Current implementation does not perform OCR, GIS export, media capture, semantic analysis, periodic source revalidation or automatic cross-repository sharding.

## Operation
The initial commit triggers one bounded run. Additional runs use the Actions manual Run workflow control and resume the saved queue. There is no schedule, paid storage, LFS, Pages deployment or automatic repository creation. status.json and ledger.jsonl contain measured run outcomes after a successful publication commit. Workflow failure may leave the prior checkpoint unchanged; the Actions log must be inspected before treating status as current.
