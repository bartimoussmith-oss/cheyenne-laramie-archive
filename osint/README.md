# Eight Cheyenne and Laramie County civic OSINT runs

These runs retrieve evidence passages from the already-preserved public corpus. They are deterministic text-retrieval and research-triage tools, not autonomous investigators, live web searches, verified legal analysis or allegations. No paid model/API, extra crawler, login, credentials, external upload or personal-dossier generation.

## Profiles
1. Budgets, audits and public spending.
2. Contracts, bids, procurement and change orders.
3. Annexation, zoning, subdivisions and development agreements.
4. Water, wastewater, lead service lines, discharge permits and stormwater.
5. Roads, transit, pavement and infrastructure.
6. Council procedures, ordinances, resolutions and public hearings.
7. Public-safety budgets, staffing and equipment; requires a public-safety organization term as well as a resource term. This is not individual suspect or resident profiling.
8. Election administration, canvassing and official election processes; not individual voter tracking.

## Outputs and provenance
Each profile produces results/<profile>.json and results/<profile>.md; results/status.json records source revision, available/scanned representation counts, indexed source-object counts, scan truncation, matching counts and up to the first 50 parsing failures. Every exported match includes original publisher URL, ledger source hash, extracted-text hash, exact character spans, preserved-representation permalink at the checked-out Git revision, page number when available and extraction method. Original publisher URLs may subsequently change; revision-pinned repository copies provide the preserved representation. Source hashes and extraction quality are not independently reverified by this engine.

## Bounds
At most 20,000 representation files and a 120-second soft scan budget. At most the first 50 matching representations per profile, in deterministic file order, with up to three keyword-context passages each. A representation can be a page or an HTML text file, not necessarily a distinct document. Query matching uses literal case-insensitive word boundaries and flexible whitespace for phrases; it does not automatically stem words or resolve entities. Broad topic matches can be irrelevant. The combined current output folder must remain below 5,000,000 bytes or publication fails. This bound does not account for accumulated Git history.

## Schedule
One initial attempt on deployment, manual runs, a daily attempt at 07:43 UTC and an attempt after successful completion of the named continuation workflow from this repository. GitHub scheduling/concurrency can delay or replace pending jobs. Existing collector concurrency is shared to avoid concurrent publication. Runs use only public-corpus text already in the repository; missing scans, unread PDFs, audio, excluded sources and undiscovered historical records are not covered. No result claims full historical completeness.

## Interpretation
A keyword such as sole source, audit, annexation or PFAS is a search lead, never proof of illegality, misconduct, contamination or a confirmed event. Public-safety matches concern institutional resources, not guilt or risk scores for individuals. The workflow does not generate accusations, infer hidden relationships or merge people by name. Reports must be reviewed against complete source documents and contrary evidence before publication as findings.

## Capacity and testing
The previously read continuation checkpoint reported 299,335,314 working-content bytes, near the 300,000,000-byte collection pause. This is a historical measurement, not an assertion of current storage. These scans avoid duplicating originals, but additional raw acquisition may still need a separately approved data partition. No paid services, purchases, LFS or billing changes are enabled. Local fixtures verified syntax, emission of eight profile reports, flexible phrase whitespace, public-safety conjunction matching and exact evidence spans. Fixtures are not real county findings. Live runs and result counts remain unverified before deployment.
