# Export the earnings-transcript Parquet to CSV for use in R.
#
# Run inside the venv:   source .venv/bin/activate && python3 snp_export_csv.py
#
# The full file is 1.82 GB on disk and ~3.5 GB uncompressed, but 99.99% of that
# is two free-text columns (`content` and `structured_content`). The metadata
# columns together are under a megabyte, so we write two files:
#
#   data/snp_meta.csv     every row, metadata only          -- small, safe in R
#   data/snp_sample.csv   N rows, metadata + full transcript -- for text work
#
# Writing all 33,362 transcripts to CSV would produce a ~1.8 GB file that
# readr cannot load on an 8 GB machine. Use Parquet + arrow for that instead.

import os

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

REPO = "Bose345/sp500_earnings_transcripts"
FILE = "parquet_files/part-0.parquet"

META = ["symbol", "company_name", "company_id", "year", "quarter", "date"]
SAMPLE_N = 500

os.makedirs("data", exist_ok=True)
path = hf_hub_download(REPO, FILE, repo_type="dataset")
pf = pq.ParquetFile(path)

# --- metadata for every row ------------------------------------------------
# Reading only these columns never touches the big text columns on disk.
meta = pf.read(columns=META).to_pandas()
meta.to_csv("data/snp_meta.csv", index=False)

# --- a sample with the transcript text -------------------------------------
# iter_batches stops after the first batch, so we read one row group at most.
batch = next(pf.iter_batches(batch_size=SAMPLE_N, columns=META + ["content"]))
batch.to_pandas().to_csv("data/snp_sample.csv", index=False)

for f in ("data/snp_meta.csv", "data/snp_sample.csv"):
    print(f"{f:<24}{os.path.getsize(f) / 1e6:>8.1f} MB")
print(f"{'rows in meta':<24}{len(meta):>8,}")
