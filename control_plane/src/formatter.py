import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from .models import HourlyStat

class Formatter:
    @staticmethod
    def print_text(schedule: List[HourlyStat]):
        for slot in schedule:
            hour_str = f"{slot.hour:02d}:00"
            
            # We preserve insertion order for determinism
            breakdown_parts = [f"{k}={v}" for k, v in slot.breakdown.items()]
            breakdown_str = ", ".join(breakdown_parts)
            
            if breakdown_str:
                line = f"{hour_str} total={slot.total_agents}; {breakdown_str}"
            else:
                line = f"{hour_str} total=0; none"
                
            print(line)

    @staticmethod
    def print_json(schedule: List[HourlyStat]):
        output = []
        for slot in schedule:
            output.append({
                "hour": slot.hour,
                "total_agents": slot.total_agents,
                "breakdown": slot.breakdown
            })
        print(json.dumps(output, indent=2))

    @staticmethod
    def save_csv(schedule: List[HourlyStat], output: Optional[str] = None):
        """Save schedule as CSV.

        If `output` is provided, write to that exact path. Otherwise create `outputs/` and
        write a timestamped file there.
        """
        # Get all unique customer names from breakdown
        all_customers = set()
        for slot in schedule:
            all_customers.update(slot.breakdown.keys())
        all_customers = sorted(all_customers)

        if output:
            output_file = Path(output)
            output_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Create outputs directory if it doesn't exist
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"schedule_{timestamp}.csv"

        # Write CSV
        with open(output_file, 'w', newline='') as f:
            fieldnames = ['hour', 'total_agents'] + all_customers
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for slot in schedule:
                row = {
                    'hour': f"{slot.hour:02d}:00",
                    'total_agents': slot.total_agents
                }
                # Add breakdown for each customer
                for customer in all_customers:
                    row[customer] = slot.breakdown.get(customer, 0)
                writer.writerow(row)

        print(f"CSV output saved to {output_file}")
