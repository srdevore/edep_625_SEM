# Dataset: https://huggingface.co/datasets/Bose345/sp500_earnings_transcripts
#
# ---------------------------------------------------------------------------
# ONE-TIME SETUP -- run these in the TERMINAL, not here.
# (Debian ships Python in pieces; this container lacks the venv package,
#  and apt needs root. Codespaces gives our user passwordless sudo.)
#
#   sudo apt-get update
#   sudo apt-get install -y python3.12-venv
#
#   python3 -m venv .venv
#   source .venv/bin/activate     # re-run this in every new terminal
#   pip install datasets
#

#
# ---------------------------------------------------------------------------
# v1 -- the canonical datasets API. Kept for reference. Downloads 1.8GB the
# first time (already done, now in ~/.cache/huggingface), then dies with
# "Terminated" during split generation on an 8GB machine. 

#   from datasets import load_dataset
#
#   ds = load_dataset("Bose345/sp500_earnings_transcripts")
#
#   print(ds)              # splits, row counts, column names
#   print(ds["train"][0])  # first record -- dumps a full transcript
#
# ---------------------------------------------------------------------------
# v2 -- streaming. Lazily reads rows from the remote Parquet, so memory stays
# flat and there is no split generation step. No len() and no ds[0]; you
# iterate, or use .take(n) / .skip(n) / .shuffle(buffer_size=...).
#
#   from datasets import load_dataset
#
#   ds = load_dataset(
#       "Bose345/sp500_earnings_transcripts",
#       split="train",
#       streaming=True,
#   )
#
#   for i, row in enumerate(ds):
#       if i == 0:
#           print(row.keys())
#       print(row["transcript"][:300], "...\n")
#       if i >= 4:
#           break
#
# ---------------------------------------------------------------------------
# v3 -- read the cached Parquet directly. What runs below.
# ---------------------------------------------------------------------------

import os

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

REPO = "Bose345/sp500_earnings_transcripts"
FILE = "parquet_files/part-0.parquet"

# Already in ~/.cache/huggingface, so this returns a local path instantly.
path = hf_hub_download(REPO, FILE, repo_type="dataset")
pf = pq.ParquetFile(path)

# --- size -----------------------------------------------------------------
md = pf.metadata
print(f"file        {path}")
print(f"on disk     {os.path.getsize(path) / 1e9:.2f} GB")
print(f"rows        {md.num_rows:,}")
print(f"columns     {md.num_columns}")
print(f"row groups  {md.num_row_groups}")

# --- column names and types ----------------------------------------------
print("\nschema")
for field in pf.schema_arrow:
    print(f"  {field.name:<24} {field.type}")

# --- one example row ------------------------------------------------------
# batch_size=1 keeps this to a single small read instead of loading the file.
row = next(pf.iter_batches(batch_size=1)).to_pylist()[0]

print("\nfirst row (values truncated to 300 chars)")
for key, value in row.items():
    text = str(value)
    print(f"\n  {key}  (len={len(text):,})")
    print(f"    {text[:300]}")


path = hf_hub_download(REPO, FILE, repo_type="dataset")
pf = pq.ParquetFile(path)

# Grab just the first 20 rows without reading the whole file
first_batch = next(pf.iter_batches(batch_size=20))
df = first_batch.to_pandas()

print(df.shape)   # (20, num_columns)
df.to_csv("sp500_first20.csv", index=False)


