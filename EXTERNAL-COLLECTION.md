# Scoped external collection

This workflow attempts real read-only copying from the county Legistar HTML calendar and links, the public ArcaSearch commissioner-minutes collection under /uswylrc/, its county-hosted guide, and one verified GIS service-metadata endpoint. A deployment commit triggers one bounded attempt; later continuation is manual. No paid tools, credentials, billing changes, subscriptions, LFS or automatic repository creation.

## Boundaries
The ArcaSearch recorded-document collection /uswylre/ and all other tenants are outside scope. No forms, JavaScript execution, login, CAPTCHA bypass, undocumented viewer internals or unrestricted domain expansion. Six URL-scope fixtures passed, including ordinary and encoded parent-directory escapes. HTML link fixtures passed for PDF, video and caption links. Live collection from these hosts has not been tested before deployment.

## Preservation
Original bodies are hashed and stored in the shared objects directory and provenance ledger. PDFs feed the connected page processor. Direct media/caption files on approved hosts may be saved when the response is under 45,000,000 bytes. External CDNs, YouTube, streaming playlists and oversized media remain explicit gaps; no full media archive is claimed. robots.txt is required and respected. Missing/blocked robots, redirects and inaccessible resources fail closed.

## Bounded operation
The adapter permits at most 100 HTTP requests including robots, a ten-minute soft collection budget, and conservatively pauses before the measured objects/text/derived working set would exceed 350,000,000 bytes with another maximum-size response. Git history and other files are not included in this budget. Captured/failed URLs and discovered external candidates are recorded. Failed URLs require review and explicit requeue; this is not automatic retry completion. Both workflows share the same concurrency group to serialize their source/data commits.

## Remaining consequential gaps
This is scoped HTML traversal, not a verified complete ArcaSearch or Legistar enumeration adapter. Form-only search/pagination and event-item API attachments may remain undiscovered. The research fetch of ArcaSearch and a candidate Legistar API request failed. No working API is asserted. The GIS metadata endpoint responded with Query capability, publisher copyright text and exportTilesAllowed=false; these are technical/publication signals, not authorization to redistribute feature databases. No GIS features, imagery or tiles are exported by this workflow. Additional repositories will require actual measured partition targets and an approved publication action. Do not label this commit as completion of all historical, GIS or media holdings.

## Results
Read external-status.json for this collector and derived-status.json for page processing; the older status.json describes the original government-host collector only. Check individual failures in ledger.jsonl. An empty queue or completed workflow is never a historical completeness certificate.
