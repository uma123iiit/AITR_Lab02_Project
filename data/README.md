# data/ — source provenance and licence audit

Raw SciFact data are **not included** in this package. They were intentionally excluded from the distributable archive.

## Acquisition record

- Source used by the archived run: official AllenAI SciFact S3 archive: https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz
- Official repository: https://github.com/allenai/scifact
- Download time recorded by the project (UTC): 2026-10-30T12:59:41Z
- Archive SHA-256 recorded by the project: `11c621288d41ac144d29b13b0f8503b3820b7d6e8b1f6ff24dff335c196d76be`
- Immutable upstream commit/release identifier: **not recorded**; `release/latest` is a moving pointer. The archived hash identifies the downloaded byte artifact in the original project record, but the original tarball is not in this submission for independent re-hashing.
- Locally recorded counts: 809 training claims, 300 development claims, 300 test claims (test labels unavailable), and 5,183 corpus abstracts. These are the files observed by the local project audit, not an assertion that all mirrors use the same split layout.

## Component-specific licence information

The official AllenAI SciFact repository's `LICENSE.md` states: claims and evidence annotations in `claims_*.jsonl` are CC BY 4.0; abstracts in `corpus.jsonl` are part of Semantic Scholar S2ORC and licensed under ODC-By 1.0; repository code is Apache 2.0. See https://github.com/allenai/scifact/blob/master/LICENSE.md.

A separate Hugging Face dataset mirror/card reports `cc-by-nc-2.0` and exposes a different split description (1,261 train / 450 validation / 300 test in the card). That mirror was **not** the source used for the archived experiment and its metadata should not be substituted for the official S3 source. See https://huggingface.co/datasets/allenai/scifact.

## Current disposition

The component-level terms for the official repository have been identified, so the earlier blanket statement that all component licences were unknown is superseded. The exact S3 archive cannot yet be mapped to an immutable upstream commit because the acquisition URL was `release/latest`. Accordingly, licence association for the exact downloaded snapshot is **partially resolved, not fully closed**. Keep all raw data local and out of public distribution until the student confirms the applicable licence notice for the exact archive snapshot and any attribution obligations. The original tarball is absent from this ZIP; do not claim its archive hash was independently rechecked in this audit.

## Recreate locally

Run `scripts/01_download_data.sh` from the repository root to fetch the current official archive and print its SHA-256. Note that this downloads the *current* `release/latest` artifact, which may not be byte-identical to the 2026-10-30 snapshot. For exact reproduction, compare against the recorded hash and stop if it differs; do not silently substitute a new snapshot.


## Primary-source recheck (02 November 2026)

The official repository README was rechecked for file/split descriptions and the official `LICENSE.md` was rechecked for component-level licence statements. The official repository lists `claims_train.jsonl`, `claims_dev.jsonl`, `claims_test.jsonl` and `corpus.jsonl`; its licence file distinguishes the claim/evidence annotations, corpus abstracts and code terms described above. This verifies the repository's current stated terms, but does not make the historical `release/latest` archive immutable. The original archived tarball is not in this submission and its recorded hash was not independently recomputed here.