import pandas as pd

p6 = pd.read_parquet("data/features/synthetic_media/unified_media_risk.parquet")
print("P6 model_versions:", p6["model_version"].unique().tolist())

p7 = pd.read_parquet("data/features/crisis_information/unified_crisis_intelligence.parquet")
dup_mask = p7["content_id"].duplicated(keep=False)
print("P7 duplicates count:", dup_mask.sum())
print("P7 total rows:", len(p7))
print("P7 unique content_ids:", p7["content_id"].nunique())
if dup_mask.sum() > 0:
    print("Sample P7 duplicates:")
    print(p7[dup_mask][["content_id", "source_dataset", "source_record_id", "event_id"]].head(10))

comp_id = p7["content_id"] + "_" + p7["event_id"].astype(str)
print("Composite key (content_id + event_id) duplicates:", comp_id.duplicated().sum())

# If index-based record_id:
rec_id = "crisis_" + p7.index.astype(str)
print("Index-based record_id duplicates:", rec_id.duplicated().sum())
