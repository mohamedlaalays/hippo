# Scheduler Visualization

Interactive 24-hour grid dashboard for visualizing agent scheduling.

## Features

- **24-hour grid view**: Each hour shows total agents needed
- **Color coding**: Visual intensity based on agent count (low/medium/high)
- **Per-customer breakdown**: Click any hour to see which customers need agents and how many
- **Statistics**: Peak hour, average agents, total customers at a glance
- **Multiple formats**: Load JSON or CSV schedule files
- **Auto-load**: Automatically loads the most recent schedule if available

## Usage

### Quick Start

1. From the `control_plane` directory, generate a schedule:
   ```bash
   make run INPUT=inputs/sample_input.csv FORMAT=json
   ```

2. Open the visualization in your browser:
   ```bash
   # Start a simple HTTP server
   cd ui
   python3 -m http.server 8000
   ```

3. Navigate to `http://localhost:8000` in your browser

### Loading Different Schedules

- **Auto-load**: The dashboard automatically loads `../outputs/schedule_20251201_102202.csv` on page load if it exists
- **Manual upload**: Click "📁 Load Schedule" to select a JSON or CSV file from anywhere

### File Formats

#### JSON Format
```json
[
  {
    "hour": 0,
    "total_agents": 0,
    "breakdown": {
      "CustomerA": 50,
      "CustomerB": 25
    }
  },
  ...
]
```

#### CSV Format
```csv
hour,total_agents,Customer1,Customer2,Customer3
00:00,0,0,0,0
01:00,100,50,30,20
...
```

## Features Explained

### Grid Cells
- **Color intensity**: Darker background = more agents needed
- **Number**: Total agents scheduled for that hour
- **Subtitle**: Number of customers requiring agents
- **Hover**: Shows "Click for details" tooltip

### Modal Details
- Click any hour to see detailed breakdown by customer
- Customers sorted by agent count (highest first)
- Quick reference for who's staffing which hours

### Statistics
- **Total Agents (Max Hour)**: Peak agent requirement across all hours
- **Average Agents**: Mean agents needed across all hours
- **Customers**: Unique number of customers in the schedule
- **Peak Hour**: Hour with highest agent requirement

## Keyboard & Interaction

- **Click hour cell**: Open modal with customer breakdown
- **Click close (×)**: Close modal
- **Click outside modal**: Close modal
- **File upload**: Supports drag-and-drop if your browser supports it
