# Acquisition extensions and verified limitations

These are tools, not evidence that any live export has completed. No adapter is connected to the collection workflow by this commit. No new repository, paid service, secret, billing setting or external-data publication is created.

## Workbook
All 29 sheets of the attached workbook were scanned locally without executing formulas. Initial keyword matches: 62 rows. Eight out-of-state name collisions were excluded, leaving 54 candidate rows and 47 normalized literal/hyperlink endpoints. These include duplicate entity representations, private providers and statewide services, not 54 independently verified local agencies. See workbook-audit.json. Reproduce full cell provenance with: python scripts/reconcile.py INPUT.xlsx OUTPUT.json . Requires openpyxl. The original workbook is not committed.

## GIS
Run python scripts/adapters.py gis JOB.json OUTPUT_DIR . A job requires approved_for_copy=true, a nonempty rights_basis, allowed_hosts and layer_url. Exports layer metadata, object IDs and batches of original Esri JSON including geometry; reconciles batch IDs and final ID sets. Does not promise an atomic attribute snapshot, attachments, related tables, imagery, automatic layer discovery or complete exports above the bounded request allowance. County GIS reuse requires review: https://www.laramiecountywy.gov/Resident-Services/GISMaps .

## Contemporary historical records
Legistar mode requires an independently verified events_api, approved hosts and copying rights. It enumerates events in pages of 100 and writes a resume offset and document/media URL manifests. It does not fetch event-item attachments or infer missing agenda packets. Calendar verified as a public discovery source: https://laramiecounty.legistar.com/Calendar.aspx . No API URL is guessed or enabled here.

## ArcaSearch
The county identifies https://gov.arcasearch.com/uswylrc/ as its public historical commissioner-minutes collection for January 1868 through June 1994. The research fetch failed; a working ArcaSearch enumeration adapter has NOT been implemented or tested. Its official guide describes browse results in 25-page groups and downloadable PDFs: https://www.laramiecountywy.gov/files/sharedassets/public/v/1/commissioners/documents/arcasearch-guide.pdf . Do not confuse this collection with the separately hosted recorded-document research system.

## OCR
OCR mode requires local_pdf and installed free executables pdftotext, pdftoppm and tesseract. It first attempts native PDF extraction; sparse documents receive bounded English OCR in requested batches of at most 20 pages. OCR is unverified derived text. Mixed scanned/text PDFs and whole-document page reconciliation remain future work. Syntax checked; executable integration not tested in this environment.

## Media
Media mode copies only explicitly approved direct_download_urls, preserves bytes and SHA-256 provenance and limits each response to 45,000,000 bytes. It is not a YouTube downloader, streaming/HLS collector, transcription engine or workaround for platform restrictions. Oversized responses fail rather than silently truncate.

## Partitions
Partition mode takes local_root and optional partition_bytes (default 350,000,000) and produces deterministic proposed shard manifests with per-file hashes. It does not create or publish repositories or move originals. Files above 45,000,000 bytes require separate lossless-chunk handling. Actual repository targets, full content and cross-repository credentials must be resolved and approved before publication. No automatic billing or paid storage.

## Tests actually performed
Python syntax compilation passed. A synthetic two-file partition fixture preserved both files across two size-bounded proposals. Copy approval was enforced in a negative test. A synthetic GIS fixture reconciled two object IDs and reported complete. Synthetic fixtures are code tests, never claimed as real county data. Workbook reconciliation ran against the actual attached workbook. Live GIS/Legistar/media network jobs, actual OCR, repository publication and ArcaSearch enumeration were not run.

## Current collection status
At the time of this preparation, status.json was still absent in the control repository. This does not establish whether the first workflow is queued, running or failed; do not claim captured-record totals without a published checkpoint or verified execution log.
