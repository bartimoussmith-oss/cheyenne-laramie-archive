# Automatic bounded continuation

This workflow resumes known work without requiring a chat message for each small batch. It is configured for one initial deployment run, manual runs, and scheduled attempts every six hours at minute 17 UTC. GitHub may delay scheduled jobs; there is no guaranteed completion time or always-running agent.

## Work per attempt
At most four rounds run, each retaining the existing 120-request government collector limit and processing up to 200 missing PDF pages across at most 50 PDFs, with no more than 50 pages per PDF in one processing pass and an eight-minute soft processing budget. The external repair/collector is attempted once, in the first round. Actual throughput may be lower. Original records and per-page provenance remain preserved. Checkpoints are committed after each round. Maximum workflow duration is 150 minutes.

## Stop conditions and spending
Known idle queues, a 300,000,000-byte objects/text/derived working-content threshold, or the PDF processor's separate 100,000,000-byte derived-storage threshold pause useful work. Repository history, all metadata and transient render sizes are not fully accounted by these thresholds. The workflow performs no purchase, paid API call, billing change, LFS configuration, secret installation or automatic repository creation. It uses standard public-repository runners and free local Poppler/Tesseract executables. Account billing settings are not verified or changed. A future capacity pause requires a separately approved publication/partition action, not a storage purchase.

## Completeness remains evidence-based
continuation-status.json distinguishes government URLs, external URLs, incomplete PDF objects and capacity pauses. Empty known queues do not establish exhaustive discovery. Form-only historical pagination, GIS republication rights, unverified vendor interfaces, streaming media and oversized files remain gaps; all_sources_complete stays false. A successful run never certifies all municipal or county holdings. Existing failures are not automatically erased, and previously failed government URLs are not automatically retried by this change.

## Tests actually performed
The revised processor passed syntax checks and a real Poppler integration test against a generated three-page native-text fixture: a two-page test budget was enforced, a second pass resumed the remaining page, and page-count reconciliation completed. This fixture is not county data. Tesseract was not installed in the local test environment and was not integration-tested there. Live workflow execution and published results require post-deployment verification. The progress assessor and scheduled workflow are newly prepared and have not been live-tested.
