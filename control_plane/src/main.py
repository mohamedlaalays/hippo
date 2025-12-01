import argparse
from .parser import InputParser
from .scheduler import Scheduler
from .formatter import Formatter


def main():
    parser = argparse.ArgumentParser(description="Call Scheduler Control Plane")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--utilization", type=float, default=1.0, help="Agent utilization (0.1 to 1.0)") # do validation on the this
    parser.add_argument("--format", choices=["text", "json", "csv"], default="text", help="Output format")
    parser.add_argument("--output", help="Path to output CSV file (only used when --format=csv)")
    
    args = parser.parse_args()

    # 1. Parse
    requirements = InputParser.parse_csv(args.input)
    
    # 2. Schedule
    scheduler = Scheduler(utilization=args.utilization)
    scheduler.process_requirements(requirements)
    
    # 3. Output
    if args.format == "json":
        Formatter.print_json(scheduler.schedule)
    elif args.format == "csv":
        Formatter.save_csv(scheduler.schedule, output=args.output)
    else:
        Formatter.print_text(scheduler.schedule)


if __name__ == "__main__":
    main()