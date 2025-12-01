import argparse
import csv
import math
import sys
import json
from typing import List, Dict
from .models import CallRequirement, HourlyStat

class Scheduler:
    def __init__(self, utilization: float = 1.0):
        self.utilization = utilization
        # 0-23 hour buckets
        self.schedule = [HourlyStat(hour=h) for h in range(24)]

    def process_requirements(self, requirements: List[CallRequirement]):
        for req in requirements:
            self._schedule_requirement(req)

    def _schedule_requirement(self, req: CallRequirement):
        # 1. Calculate agents needed per hour for this specific customer
        # Formula: ceil(calls_per_hour * avg_duration / 3600 / utilization) 
        
        calls_per_hour = req.calls_per_hour
        
        # Protect against div by zero if utilization is passed as 0.0
        util_factor = max(self.utilization, 0.01)
        
        # Calculate raw workload in agent-seconds required per hour
        workload_seconds = calls_per_hour * req.avg_duration_sec
        
        # Capacity of one agent in seconds (3600 * utilization)
        agent_capacity = 3600 * util_factor
        
        agents_needed = math.ceil(workload_seconds / agent_capacity)

        # 2. Fill the buckets 
        # Start inclusive, End exclusive
        for hour in range(req.start_hour, req.end_hour):
            bucket = self.schedule[hour]
            bucket.total_agents += agents_needed
            bucket.breakdown[req.customer_name] = agents_needed
