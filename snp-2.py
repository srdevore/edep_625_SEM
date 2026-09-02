

from datasets import load_dataset
ds = load_dataset("Bose345/sp500_earnings_transcripts")
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
