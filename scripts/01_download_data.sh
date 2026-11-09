set -euo pipefail
D=data/raw/scifact; mkdir -p $D; cd $D        # own empty dir: archive is untrusted until audited
URL="https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz"   # from the official repo README; re-verify at https://github.com/allenai/scifact
curl -fL --retry 3 -o data.tar.gz "$URL"
echo "$URL" > source_url.txt; date -u +%FT%TZ > download_date_utc.txt
sha256sum data.tar.gz | tee data.tar.gz.sha256
tar -tzf data.tar.gz > tar_listing.txt; head -20 tar_listing.txt   # inspect member paths before extracting (no pipe: head would trip pipefail)
tar -xzf data.tar.gz
find . -name '*.jsonl' | sort | xargs wc -l
sha256sum $(find . -name '*.jsonl' | sort) > jsonl.sha256