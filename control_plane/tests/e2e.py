#!/usr/bin/env python3
"""End-to-end test: run scheduler with CSV output and compare to ground truth.
"""
import subprocess
import sys
import csv
from pathlib import Path
from termcolor import colored

def read_csv(path: Path):
    with path.open(newline='') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
    return rows


def main():
    script_dir = Path(__file__).resolve().parent

    data_dir = script_dir / "data"
    input_csv = data_dir / "e2e_input.csv"
    ground_truth = data_dir / "e2e_ground_truth.csv"
    produced_path = data_dir / "e2e_output.csv"

    if not input_csv.exists():
        print(colored(f"Error: input file not found: {input_csv}", 'red'))
        sys.exit(2)
    if not ground_truth.exists():
        print(f"Error: ground truth file not found: {ground_truth}")
        sys.exit(2)


    data_dir.mkdir(exist_ok=True)

    # Run the program to produce CSV output at a known path inside tests/data
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "src.main", "--input", str(input_csv), "--format", "csv", "--output", str(produced_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print("Program failed to run:\n", e.stdout, e.stderr)
        sys.exit(3)

    produced = produced_path

    if not produced.exists():
        print("Error: could not find produced CSV (expected at", produced_path, ")")
        sys.exit(4)

    print(f"Produced CSV: {produced}")

    # Read both CSVs and compare rows exactly
    produced_rows = read_csv(produced)
    truth_rows = read_csv(ground_truth)

    if produced_rows != truth_rows:
        #print in red
        print(colored("E2E Test FAILED: produced CSV does not match ground truth", 'red'))

        # Find first differing row
        print(f"Produced rows: {len(produced_rows)}, Ground truth rows: {len(truth_rows)}")
        min_len = min(len(produced_rows), len(truth_rows))
        for i in range(min_len):
            if produced_rows[i] != truth_rows[i]:
                print("Difference found at row index:", i)
                print("Produced row:", produced_rows[i])
                print("Ground truth row:", truth_rows[i])
                break

        # Clean up produced file
        try:
            produced.unlink()
        except Exception:
            pass
        sys.exit(1)

    # Clean up produced file
    try:
        produced.unlink()
    except Exception as e:
        print(f"Warning: could not delete produced file: {e}")

    print(colored("E2E Test PASSED: produced CSV matches ground truth", 'green'))
    sys.exit(0)


if __name__ == '__main__':
    main()
