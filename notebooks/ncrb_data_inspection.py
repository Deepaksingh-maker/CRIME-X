from pathlib import Path
import pandas as pd


# ============================================================
# CRIMEX - NCRB DATA INSPECTION
# ============================================================

# Project root = CRIME X
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# NCRB data folder
DATA_DIR = PROJECT_ROOT / "data" / "ncrb 2022"

# Output folder
OUTPUT_DIR = PROJECT_ROOT / "data" / "inspection"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("CRIMEX - NCRB 2022 DATA INSPECTION")
print("=" * 70)

print(f"\nProject folder : {PROJECT_ROOT}")
print(f"NCRB folder    : {DATA_DIR}")


# ------------------------------------------------------------
# 1. FIND ALL CSV FILES
# ------------------------------------------------------------

csv_files = list(DATA_DIR.rglob("*.csv"))

print(f"\nTotal CSV files found: {len(csv_files)}")

if len(csv_files) == 0:
    print("\nERROR: No CSV files found.")
    print("Check the path:")
    print(DATA_DIR)
    raise SystemExit


# ------------------------------------------------------------
# 2. INSPECT EVERY CSV
# ------------------------------------------------------------

results = []

for i, file_path in enumerate(csv_files, start=1):

    try:
        df = pd.read_csv(
            file_path,
            encoding="utf-8",
            low_memory=False
        )

    except UnicodeDecodeError:
        try:
            df = pd.read_csv(
                file_path,
                encoding="latin1",
                low_memory=False
            )
        except Exception as e:
            print(f"\nCould not read: {file_path.name}")
            print(e)
            continue

    except Exception as e:
        print(f"\nCould not read: {file_path.name}")
        print(e)
        continue

    columns = list(df.columns)

    # Convert column names to lowercase for searching
    column_text = " ".join(
        str(col).lower() for col in columns
    )

    # Detect useful concepts
    has_state = any(
        word in column_text
        for word in ["state", "states"]
    )

    has_district = any(
        word in column_text
        for word in ["district"]
    )

    has_crime = any(
        word in column_text
        for word in ["crime", "offence", "offense"]
    )

    has_year = any(
        word in column_text
        for word in ["year"]
    )

    has_location = any(
        word in column_text
        for word in ["location", "place", "latitude", "longitude"]
    )

    results.append({
        "file_name": file_path.name,
        "file_path": str(file_path.relative_to(PROJECT_ROOT)),
        "rows": len(df),
        "columns_count": len(columns),
        "columns": " | ".join(columns),
        "has_state": has_state,
        "has_district": has_district,
        "has_crime": has_crime,
        "has_year": has_year,
        "has_location": has_location
    })

    print(
        f"[{i}/{len(csv_files)}] "
        f"{file_path.name} "
        f"→ {len(df)} rows × {len(columns)} columns"
    )


# ------------------------------------------------------------
# 3. CREATE MASTER INSPECTION REPORT
# ------------------------------------------------------------

report = pd.DataFrame(results)

report_path = OUTPUT_DIR / "ncrb_table_inventory.csv"

report.to_csv(
    report_path,
    index=False,
    encoding="utf-8-sig"
)

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)

print(f"\nReport saved at:")
print(report_path)

print("\nSummary:")
print(f"Tables successfully inspected : {len(report)}")
print(
    f"Tables with State information : "
    f"{report['has_state'].sum()}"
)
print(
    f"Tables with District info     : "
    f"{report['has_district'].sum()}"
)
print(
    f"Tables with Crime information : "
    f"{report['has_crime'].sum()}"
)
print(
    f"Tables with Year information  : "
    f"{report['has_year'].sum()}"
)
print(
    f"Tables with Location info     : "
    f"{report['has_location'].sum()}"
)

print("\nNext step:")
print("Open:")
print(report_path)