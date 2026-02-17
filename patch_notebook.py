"""Patch indoor_Microsoft notebook: add subdir support and leftover-sites conversion."""
import re

path = r"indoor_Microsoft_flow_real_data - all sites flow mutual.ipynb"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. get_sites_from_preprocessed_data: add subdir=None to signature only (body already has if subdir)
old1 = '"def get_sites_from_preprocessed_data(data_root, floor):\\n",'
new1 = '"def get_sites_from_preprocessed_data(data_root, floor, subdir=None):\\n",'
if old1 in content:
    content = content.replace(old1, new1)
    print("Patched get_sites_from_preprocessed_data signature")
else:
    print("Pattern 1 not found (maybe already patched?)")

# 2. read_preprocessed_signals_data: add preprocessed_subdir param
old2 = '"def read_preprocessed_signals_data(data_root, site, floor):\\n",\n        "    out_path = Path(data_root) / \\"preprocessed_data_thesis\\" / f\\"wifi_fp_{site}_{floor}.csv\\"\\n",'
new2 = '"def read_preprocessed_signals_data(data_root, site, floor, preprocessed_subdir=None):\\n",\n        "    base = Path(data_root) / \\"preprocessed_data_thesis\\"\\n",\n        "    out_path = (base / preprocessed_subdir / f\\"wifi_fp_{site}_{floor}.csv\\") if preprocessed_subdir else (base / f\\"wifi_fp_{site}_{floor}.csv\\")\\n",'
if old2 in content:
    content = content.replace(old2, new2)
    print("Patched read_preprocessed_signals_data")
else:
    print("Pattern 2 not found")

# 3. Add get_sites_from_sites_to_run and get_leftover_sites_to_run after get_sites_from_preprocessed_data (before compute_prediction_error)
old3 = '"    return sorted(sites)\\n",\n        "\\n",\n        "def compute_prediction_error(true_locations, predicted_locations):\\n",'
new3 = '"    return sorted(sites)\\n",\n        "\\n",\n        "def get_sites_from_sites_to_run(sites_to_run_dir):\\n",\n        "    \\\"\\\"\\\"Return site IDs from folder with files named {site}_1000_train.csv.\\\"\\\"\\\"\\n",\n        "    return get_sites_from_train_folder(sites_to_run_dir)\\n",\n        "\\n",\n        "def get_leftover_sites_to_run(sites_to_run_dir, data_root, floor):\\n",\n        "    \\\"\\\"\\\"Sites in sites_to_run that are not yet in preprocessed_data_thesis (root).\\\"\\\"\\\"\\n",\n        "    in_run = set(get_sites_from_sites_to_run(sites_to_run_dir))\\n",\n        "    done = set(get_sites_from_preprocessed_data(data_root, floor))\\n",\n        "    return sorted(in_run - done)\\n",\n        "\\n",\n        "def compute_prediction_error(true_locations, predicted_locations):\\n",'
if old3 in content:
    content = content.replace(old3, new3)
    print("Patched added get_sites_from_sites_to_run and get_leftover_sites_to_run")
else:
    print("Pattern 3 not found")

# 4. Replace the new_sites cell with leftover_sites + dirs (so next cell can use them)
old4 = '"new_sites = get_sites_from_train_folder(fr\\"C:\\\\Users\\\\Noa\\\\Documents\\\\GitHub\\\\indoor_localization_research\\\\preprocessed_data_thesis\\\\sites_to_run\\")"'
new4 = '"SITES_TO_RUN_DIR = Path(data_root) / \\"preprocessed_data_thesis\\" / \\"sites_to_run\\"\\n",\n        "LEFTOVER_OUT_DIR = Path(data_root) / \\"preprocessed_data_thesis\\" / \\"leftover sites to run\\"\\n",\n        "LEFTOVER_OUT_DIR.mkdir(parents=True, exist_ok=True)\\n",\n        "leftover_sites = get_leftover_sites_to_run(str(SITES_TO_RUN_DIR), data_root, FLOOR)\\n",\n        "print(f\\"Leftover sites to convert: {len(leftover_sites)}\\")\\n",\n        "new_sites = leftover_sites\\n",'
if old4 in content:
    content = content.replace(old4, new4)
    print("Patched: SITES_TO_RUN_DIR, LEFTOVER_OUT_DIR, leftover_sites")
else:
    print("Pattern 4 not found")

# 5. Replace build_wifi_fingerprint_df loop with convert_1000_train_to_wifi_fp (use _1000_train from sites_to_run)
old5 = '"# build_wifi_fingerprint_df expects .txt trace files under data_root/train/<site>/F<floor>/\\n",\n        "\\n",\n        "out_dir = Path(data_root) / \\"preprocessed_data_thesis\\" / \\"leftover sites to run\\"\\n",\n        "out_dir.mkdir(parents=True, exist_ok=True)\\n",\n        "\\n",\n        "for site in tqdm(new_sites, desc=\\"wifi_fp_*.csv\\"):\\n",\n        "    floor = 1\\n",\n        "    try:\\n",\n        "        df_fp = build_wifi_fingerprint_df(site, floor, data_root, metadata_root, split=\\"train\\")\\n",\n        "        df_clean = clean_wifi_df(df_fp)\\n",\n        "        out_path = out_dir / f\\"wifi_fp_{site}_{floor}.csv\\"\\n",\n        "        df_clean.to_csv(out_path, index=False)\\n",\n        "        print(f\\"  Saved {out_path.name} ({len(df_clean)} rows)\\")\\n",\n        "    except Exception as e:\\n",\n        "        print(f\\"  Skip {site} (floor {floor}): {e}\\")"'
new5 = '"# Convert _1000_train.csv (from sites_to_run) to wifi_fp_*.csv in leftover sites to run\\n",\n        "def convert_1000_train_to_wifi_fp(site, floor, sites_to_run_dir, out_dir):\\n",\n        "    path = Path(sites_to_run_dir) / f\\\\\\"{site}_1000_train.csv\\\\\\"\\n",\n        "    if not path.exists(): raise FileNotFoundError(path)\\n",\n        "    df = pd.read_csv(path)\\n",\n        "    for col in [\\\\\\"f\\\\\\", \\\\\\"path\\\\\\", \\\\\\"Unnamed: 0\\\\\\"]:\\n",\n        "        if col in df.columns: df = df.drop(columns=[col])\\n",\n        "    df_clean = clean_wifi_df(df)\\n",\n        "    out_path = Path(out_dir) / f\\\\\\"wifi_fp_{site}_{floor}.csv\\\\\\"\\n",\n        "    df_clean.to_csv(out_path, index=False)\\n",\n        "    return out_path\\n",\n        "\\n",\n        "out_dir = LEFTOVER_OUT_DIR\\n",\n        "for site in tqdm(new_sites, desc=\\"wifi_fp_*.csv\\"):\\n",\n        "    floor = FLOOR\\n",\n        "    try:\\n",\n        "        out_path = convert_1000_train_to_wifi_fp(site, floor, SITES_TO_RUN_DIR, out_dir)\\n",\n        "        print(f\\"  Saved {out_path.name} ({len(pd.read_csv(out_path))} rows)\\")\\n",\n        "    except Exception as e:\\n",\n        "        print(f\\"  Skip {site} (floor {floor}): {e}\\")"'
if old5 in content:
    content = content.replace(old5, new5)
    print("Patched: convert_1000_train_to_wifi_fp + loop")
else:
    print("Pattern 5 not found")

# 5b. run_predictions_from_saved_graphs: add preprocessed_subdir param
content = content.replace(
    '"def run_predictions_from_saved_graphs(site, floor, n_labeled_list, data_root, output_path, experiment_save_dir, N_VALIDATION=200):\\n",',
    '"def run_predictions_from_saved_graphs(site, floor, n_labeled_list, data_root, output_path, experiment_save_dir, N_VALIDATION=200, preprocessed_subdir=None):\\n",'
)
# 6. Use preprocessed_subdir in all read_preprocessed_signals_data calls
six_a = '"    df_clean = read_preprocessed_signals_data(data_root, site, floor)\\n",'
six_b = '"            df_clean = read_preprocessed_signals_data(data_root, site, floor)\\n",'
if six_a in content or six_b in content:
    content = content.replace(six_a, '"    df_clean = read_preprocessed_signals_data(data_root, site, floor, preprocessed_subdir)\\n",')
    content = content.replace(six_b, '"            df_clean = read_preprocessed_signals_data(data_root, site, floor, preprocessed_subdir)\\n",')
    print("Patched: read_preprocessed_signals_data(..., preprocessed_subdir)")
else:
    print("Pattern 6 already applied")

# 7. Add preprocessed_subdir in the config cell so it's defined before use
old7 = '"N_LABELED_LIST = [10, 15, 20]\\n",\n        "N_VALIDATION_FIXED = 200"'
if '"preprocessed_subdir = None\\n"' in content and 'N_VALIDATION_FIXED' in content:
    print("Pattern 7 already applied (preprocessed_subdir in config cell)")
elif old7 in content:
    content = content.replace(old7, '"N_LABELED_LIST = [10, 15, 20]\\n",\n        "preprocessed_subdir = None\\n",\n        "N_VALIDATION_FIXED = 200"')
    print("Patched: preprocessed_subdir in config cell")
else:
    print("Pattern 7 not found")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done.")
