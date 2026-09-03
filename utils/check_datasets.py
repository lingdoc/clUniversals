import os
import gzip

def check_linguistic_datasets():
    results_dir = "../tlu"

    if not os.path.isdir(results_dir):
        print(f" Error: Cannot find '{results_dir}' directory.")
        return

    # isolate only the numeric subfolders
    subfolders = sorted([
        f for f in os.listdir(results_dir)
        if os.path.isdir(os.path.join(results_dir, f)) and f != "BT_results_summary"
    ])

    print(f"🔬 Scanning {len(subfolders)} subfolders for accuracy...\n")
    print(f"{'Subfolder':<20} | {'Languages':<10} | {'Features':<10} | {'Trees Found':<12}")
    print("-" * 62)

    total_valid = 0

    for folder in subfolders:
        folder_path = os.path.join(results_dir, folder)
        bt_path = os.path.join(folder_path, "BT_data.txt")
        tree_path = os.path.join(folder_path, "pruned_tree.trees.gz")

        languages_count = 0
        features_count = 0
        trees_count = 0
        issue_found = False

        # parse BT_data.txt (count languages & distinct features)
        if os.path.exists(bt_path):
            try:
                with open(bt_path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

                if lines:
                    # in BayesTraits format, the first data row often dictates header structure
                    # so look at the unique values or column distributions
                    languages_count = len(lines)

                    # split columns to check for data density (assuming tab or space delimited)
                    sample_cols = lines[0].split()
                    if len(sample_cols) > 1:
                        # first column is always Language ID/Name, remainder are linguistic states
                        features_count = len(sample_cols) - 1
            except Exception as e:
                print(f"⚠️ Error reading {bt_path}: {e}")
                issue_found = True
        else:
            issue_found = True

        # parse pruned_tree.trees.gz (count trees safely without memory overflow)
        if os.path.exists(tree_path):
            try:
                with gzip.open(tree_path, "rt", encoding="utf-8") as f:
                    for line in f:
                        # BayesTraits and NEXUS tree lines typically start with 'tree'
                        if line.strip().lower().startswith("tree "):
                            trees_count += 1
            except Exception as e:
                print(f"⚠️ Error reading compressed file {tree_path}: {e}")
                issue_found = True
        else:
            issue_found = True

        # log results to terminal
        folder_display = folder if len(folder) <= 20 else folder[:17] + "..."
        print(f"{folder_display:<20} | {languages_count:<10} | {features_count:<10} | {trees_count:<12}")

        if not issue_found and languages_count > 0 and (trees_count == 100 or trees_count == 1000):
            total_valid += 1

    print("-" * 62)
    print(f" Scan Finished: {total_valid}/{len(subfolders)} dataset sets are structurally intact.")

if __name__ == "__main__":
    check_linguistic_datasets()
