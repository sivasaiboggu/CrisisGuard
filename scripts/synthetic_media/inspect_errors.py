import pandas as pd

df_part = pd.read_parquet("data/features/synthetic_media/cifake_partitions.parquet")
df_pred = pd.read_parquet("data/features/synthetic_media/image_predictions.parquet")
test_df = df_part[df_part['split'] == 'test'].reset_index(drop=True)
merged = pd.merge(test_df, df_pred, on='content_id')
merged['pred_label'] = (merged['synthetic_probability'] >= 0.5).astype(int)

fps = merged[(merged['label'] == 0) & (merged['pred_label'] == 1)]
fns = merged[(merged['label'] == 1) & (merged['pred_label'] == 0)]
tps = merged[(merged['label'] == 1) & (merged['pred_label'] == 1)]
tns = merged[(merged['label'] == 0) & (merged['pred_label'] == 0)]

print(f"TN: {len(tns)} | FP: {len(fps)} | FN: {len(fns)} | TP: {len(tps)}")
print("\nFalse Positives (Real misclassified as Synthetic):")
for idx, r in fps.iterrows():
    print(f"  {r['content_id']} | Prob: {r['synthetic_probability']} | File: {r['source_path']} | Size: {r['file_size_bytes']} bytes")

print("\nFalse Negatives (Synthetic misclassified as Real):")
for idx, r in fns.iterrows():
    print(f"  {r['content_id']} | Prob: {r['synthetic_probability']} | File: {r['source_path']} | Size: {r['file_size_bytes']} bytes")
