
import argparse
import csv
import math
import sys
import json
from typing import List, Dict
from .models import CallRequirement
from termcolor import colored
from dateutil.parser import parse
from datetime import datetime

class InputParser:
    @staticmethod
    def extract_hour(time_string: str) -> int:
        try:
            # check if time_string is int and raise error if not in 0-24 (allow 24 for end_hour)
            if time_string.isdigit():
                hour = int(time_string)
                if 0 > hour or hour > 24:
                    raise ValueError
            # dateutil intelligently guesses the format and returns a full datetime object
            dt_object = parse(time_string)
            return dt_object.hour
        except ValueError:
            raise ValueError(f"Invalid time format: {time_string}")
        
    
    @staticmethod
    def validate_columns(row: List[str]):
        expected_columns = ['CustomerName', 'AverageCallDurationSeconds', 'StartTimePT', 'EndTimePT', 'NumberOfCalls', 'Priority']
        if row is None:
            raise ValueError("CSV file is missing a header row.")
        for i, col in enumerate(expected_columns):
            if i >= len(row) or row[i].strip() != col:
                raise ValueError(f"Expected column '{col}' at position {i}, but got '{row[i] if i < len(row) else 'N/A'}'")

        
    @staticmethod
    def parse_csv(filepath: str) -> List[CallRequirement]:
        requirements = []
        try:
            with open(filepath, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                InputParser.validate_columns(header)

                for row_idx, row in enumerate(reader):
                    if not row or len(row) < 6:
                        print(colored(f"Skipping invalid or incomplete row {row_idx}", 'yellow'), file=sys.stderr)
                        continue # Skip incomplete lines
                    try:
                        # Column based mapping: Name, Duration, Start, End, Calls, Priority
                        name = row[0].strip()
                        duration = int(row[1].strip())
                        start = InputParser.extract_hour(row[2].strip())
                        end = InputParser.extract_hour(row[3].strip())
                        if end == 0: end = 24 # using assumption there is 24th hour of the day
                        calls = int(row[4].strip())
                        priority = int(row[5].strip())

                        req = CallRequirement(
                            customer_name=name,
                            avg_duration_sec=duration,
                            start_hour=start,
                            end_hour=end,
                            total_calls=calls,
                            priority=priority
                        )
                        requirements.append(req)
                        
                    except ValueError as e:
                        print(colored(f"Error parsing row {row_idx}: {e}", 'red'), file=sys.stderr)
                        continue

        except FileNotFoundError:
            print(f"Error: File {filepath} not found.", file=sys.stderr)
            sys.exit(1)
            
        return requirements
