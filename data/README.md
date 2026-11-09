# SciFact dataset — download, provenance and licence

## Download the dataset

The project uses the SciFact scientific claim-verification dataset released by AllenAI.

- **Official archive:** https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz
- **Official dataset/code repository:** https://github.com/allenai/scifact
- **Dataset schema and file descriptions:** https://github.com/allenai/scifact/blob/master/doc/data.md
- **Official licence statements:** https://github.com/allenai/scifact/blob/master/LICENSE.md
- **Hugging Face dataset mirror (not used for the archived run):** https://huggingface.co/datasets/allenai/scifact

From the project root, download the current official archive using:

```bash
bash scripts/01_download_data.sh
```

The expected core files in the official archive are `corpus.jsonl`, `claims_train.jsonl`, `claims_dev.jsonl` and `claims_test.jsonl`, with optional cross-validation splits. See the official schema documentation for field definitions.

## Acquisition record for the archived experiment

- Source used by the archived run: official AllenAI SciFact S3 archive.
- Download time recorded by the project (UTC): 2026-10-30T12:59:41Z.
- Archive SHA-256 recorded by the project: `11c621288d41ac144d29b13b0f8503b3820b7d6e8b1f6ff24dff335c196d76be`.
- Immutable upstream commit/release identifier: **not recorded**; `release/latest` is a moving pointer. The archived hash identifies the downloaded byte artifact in the original project record, but the original tarball is not in this submission for independent re-hashing.
- Locally recorded counts: 809 training claims, 300 development claims, 300 test claims (test labels unavailable), and 5,183 corpus abstracts. These are the files observed by the local project audit, not an assertion that all mirrors use the same split layout.

A new download from `release/latest` may differ from the historical snapshot. Compare its SHA-256 against the recorded value before treating it as an exact reproduction; do not silently substitute a different snapshot.

## Component-specific licence information

The official AllenAI SciFact repository's `LICENSE.md` states:
- Claims and evidence annotations in `claims_*.jsonl`: **CC BY 4.0**.
- Abstracts in `corpus.jsonl`: part of the Semantic Scholar S2ORC dataset, licensed under **ODC-By 1.0**.
- Repository code: **Apache 2.0**.

The separate Hugging Face dataset card reports `cc-by-nc-2.0` and a different split description (1,261 train / 450 validation / 300 test in the card). That mirror was **not** the source used for the archived experiment; do not substitute its metadata for the official S3 source.

## Current disposition

The component-level terms for the official repository have been identified, so the earlier blanket statement that all component licences were unknown is superseded. The exact S3 archive cannot yet be mapped to an immutable upstream commit because the acquisition URL was `release/latest`. Accordingly, licence association for the exact downloaded snapshot is **partially resolved, not fully closed**. Raw data are not committed to this repository; download them directly from the official source and retain the required attribution/licence notices. The original tarball is absent from this submission and its recorded hash was not independently recomputed here.

## Recreate locally

Run `scripts/01_download_data.sh` from the repository root to fetch the current official archive and print its SHA-256. This downloads the current `release/latest` artifact, which may not be byte-identical to the 2026-10-30 snapshot.
