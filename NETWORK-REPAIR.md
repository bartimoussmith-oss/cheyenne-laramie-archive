# Correcting the external acquisition failure

The first published external checkpoint reported zero captured records and four HTTP failures. Those messages did not identify whether robots.txt or the requested record failed. Therefore they are not proof that each source record URL is missing.

## Repair
The wrapper changes only the external adapter's fetch method. A robots.txt HTTP 404 or 410 is treated as an absent file, unless the error response contains User-agent rules, which are parsed and respected. Explicit robots disallow, HTTP 401/403/429, other non-404/410 errors and network failures still block collection. Actual record requests must still succeed and pass the existing host/path limits. Redirects remain disabled. No access-control bypass is added. Protocol reference: https://datatracker.ietf.org/doc/html/rfc9309#section-2.3.1.3 .

## Evidence and retry
network-events.jsonl identifies robots, policy and record stages separately. The Legistar calendar, public commissioner-minutes ArcaSearch seed and GIS metadata seed are requeued once per invocation for a bounded attempt. The forbidden county-hosted guide is not explicitly requeued. Existing ledger evidence is preserved. Future source failures remain visible; a workflow completing does not prove that every source was captured.

## Useful work in the same run
After the external attempt, the workflow resumes the original government-source queue and runs bounded PDF extraction/OCR plus measured partition planning. Available outputs and checkpoints are committed even if an individual stage fails, unless cancellation or infrastructure failure prevents publication. No schedule, paid service, billing change, LFS, repository creation or automatic feature-database republication. Existing per-stage request, storage and processing bounds remain in force.

## Tests actually performed
Python syntax compilation passed. Mock HTTP tests passed for absent robots 404/410, blocked 401/403/429/500 and explicit Disallow. These are synthetic behavior tests, not evidence of real captured county records. Live execution and results must be verified after deployment. Complete historical enumeration, streamed media, licensed GIS feature republication and cross-repository publication are not established by this repair.
