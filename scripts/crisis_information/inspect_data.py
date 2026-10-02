import json
from pathlib import Path
import pandas as pd
import numpy as np

def audit():
    root = Path(__file__).resolve().parent.parent.parent
    data_dir = root / "data" / "processed"
    
    datasets = ["humaid", "crisismmd", "crisislex"]
    results = {}
    
    for ds in datasets:
        pq_path = data_dir / ds / f"{ds}_records.parquet"
        if not pq_path.exists():
            print(f"[MISSING] {pq_path}")
            continue
        df = pd.read_parquet(pq_path)
        print(f"\n==========================================")
        print(f"AUDITING: {ds.upper()}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Null counts:\n{df.isnull().sum()}")
        
        info = {
            "shape": list(df.shape),
            "columns": list(df.columns),
            "nulls": {col: int(cnt) for col, cnt in df.isnull().sum().items()},
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        # Specific audits
        if ds == "humaid":
            info["split_counts"] = {k: int(v) for k, v in df["split"].value_counts().items()}
            info["category_counts"] = {k: int(v) for k, v in df["category"].value_counts().items()}
            info["event_counts"] = {k: int(v) for k, v in df["disaster_event"].value_counts().items()}
            print(f"Splits:\n{df['split'].value_counts()}")
            print(f"Categories:\n{df['category'].value_counts()}")
            
        elif ds == "crisismmd":
            info["split_counts"] = {k: int(v) for k, v in df["split"].value_counts().items()}
            info["humanitarian_label_counts"] = {k: int(v) for k, v in df["humanitarian_label"].value_counts().items()}
            info["informative_label_counts"] = {k: int(v) for k, v in df["informative_label"].value_counts().items()}
            info["disaster_event_counts"] = {k: int(v) for k, v in df["disaster_event"].value_counts().items()}
            info["image_available_locally"] = {str(k): int(v) for k, v in df["image_available_locally"].value_counts().items()}
            print(f"Splits:\n{df['split'].value_counts()}")
            print(f"Humanitarian Labels:\n{df['humanitarian_label'].value_counts()}")
            print(f"Informative Labels:\n{df['informative_label'].value_counts()}")
            print(f"Events:\n{df['disaster_event'].value_counts()}")
            print(f"Image Available Locally:\n{df['image_available_locally'].value_counts()}")
            
        elif ds == "crisislex":
            info["source_dataset_counts"] = {k: int(v) for k, v in df["source_dataset"].value_counts().items()}
            info["disaster_event_count"] = int(df["disaster_event"].nunique())
            info["informativeness_label_counts"] = {k: int(v) for k, v in df["informativeness_label"].value_counts().head(20).items()}
            info["top_disaster_events"] = {k: int(v) for k, v in df["disaster_event"].value_counts().head(10).items()}
            print(f"Source datasets:\n{df['source_dataset'].value_counts()}")
            print(f"Number of events: {df['disaster_event'].nunique()}")
            print(f"Top 10 Events:\n{df['disaster_event'].value_counts().head(10)}")
            print(f"Informativeness labels (top 10):\n{df['informativeness_label'].value_counts().head(10)}")
            
        results[ds] = info
        
    # Check overlap across datasets
    df_h = pd.read_parquet(data_dir / "humaid" / "humaid_records.parquet")
    df_c = pd.read_parquet(data_dir / "crisismmd" / "crisismmd_records.parquet")
    df_l = pd.read_parquet(data_dir / "crisislex" / "crisislex_records.parquet")
    
    h_ids = set(df_h["source_record_id"])
    c_ids = set(df_c["source_record_id"])
    l_ids = set(df_l["source_record_id"])
    
    print("\n--- Cross-Dataset Overlap ---")
    print("HumAID unique IDs:", len(h_ids))
    print("CrisisMMD unique IDs:", len(c_ids))
    print("CrisisLex unique IDs:", len(l_ids))
    print("HumAID in CrisisMMD:", len(h_ids.intersection(c_ids)))
    print("HumAID in CrisisLex:", len(h_ids.intersection(l_ids)))
    print("CrisisMMD in CrisisLex:", len(c_ids.intersection(l_ids)))
    
    results["overlap"] = {
        "humaid_in_crisismmd": len(h_ids.intersection(c_ids)),
        "humaid_in_crisislex": len(h_ids.intersection(l_ids)),
        "crisismmd_in_crisislex": len(c_ids.intersection(l_ids))
    }
    out_json = root / "docs" / "crisis_information" / "audit_stats.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved audit stats to {out_json}")

if __name__ == "__main__":
    audit()
