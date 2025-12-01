import unittest
import math
from src.scheduler import Scheduler
from src.models import CallRequirement, HourlyStat


class TestScheduler(unittest.TestCase):
    """Unit tests for the Scheduler class"""

    def setUp(self):
        """Set up test fixtures"""
        self.scheduler = Scheduler(utilization=1.0)

    def test_scheduler_initialization_default(self):
        """Test Scheduler initializes with default utilization"""
        scheduler = Scheduler()
        self.assertEqual(scheduler.utilization, 1.0)

    def test_scheduler_initialization_custom_utilization(self):
        """Test Scheduler initializes with custom utilization"""
        scheduler = Scheduler(utilization=0.8)
        self.assertEqual(scheduler.utilization, 0.8)

    def test_scheduler_schedule_creation(self):
        """Test that schedule is created with 24 hourly buckets"""
        self.assertEqual(len(self.scheduler.schedule), 24)
        for i, bucket in enumerate(self.scheduler.schedule):
            self.assertIsInstance(bucket, HourlyStat)
            self.assertEqual(bucket.hour, i)
            self.assertEqual(bucket.total_agents, 0)
            self.assertEqual(bucket.breakdown, {})

    def test_schedule_requirement_single_hour(self):
        """Test scheduling a requirement that spans a single hour"""
        req = CallRequirement(
            customer_name="Customer A",
            avg_duration_sec=600,  # 10 minutes
            start_hour=9,
            end_hour=10,
            total_calls=6,  # 6 calls in 1 hour
            priority=1
        )
        self.scheduler.process_requirements([req])
        
        # 6 calls/hour * 600 sec/call / (3600 sec * 1.0 utilization) = 1 agent
        self.assertEqual(self.scheduler.schedule[9].total_agents, 1)
        self.assertEqual(self.scheduler.schedule[9].breakdown["Customer A"], 1)

    def test_schedule_requirement_single_hour_mid_night(self):
        """Test scheduling a requirement that spans a single hour"""
        req = CallRequirement(
            customer_name="Customer Z",
            avg_duration_sec=600,  # 10 minutes
            start_hour=23,
            end_hour=24,
            total_calls=6,  # 6 calls in 1 hour
            priority=1
        )
        self.scheduler.process_requirements([req])
        
        # 6 calls/hour * 600 sec/call / (3600 sec * 1.0 utilization) = 1 agent
        self.assertEqual(self.scheduler.schedule[23].total_agents, 1)
        self.assertEqual(self.scheduler.schedule[23].breakdown["Customer Z"], 1)
    def test_schedule_requirement_single_hour_first_hour(self):
        """Test scheduling a requirement that spans a single hour"""
        req = CallRequirement(
            customer_name="Customer Y",
            avg_duration_sec=600,  # 10 minutes
            start_hour=0,
            end_hour=1,
            total_calls=6,  # 6 calls in 1 hour
            priority=1
        )
        self.scheduler.process_requirements([req])
        
        # 6 calls/hour * 600 sec/call / (3600 sec * 1.0 utilization) = 1 agent
        self.assertEqual(self.scheduler.schedule[0].total_agents, 1)
        self.assertEqual(self.scheduler.schedule[0].breakdown["Customer Y"], 1)

    def test_schedule_requirement_multiple_hours(self):
        """Test scheduling a requirement that spans multiple hours"""
        req = CallRequirement(
            customer_name="Customer B",
            avg_duration_sec=300,  # 5 minutes
            start_hour=8,
            end_hour=12,  # 4 hours
            total_calls=24,  # 6 calls per hour
            priority=2
        )
        self.scheduler.process_requirements([req])
        
        # 6 calls/hour * 300 sec/call / 3600 sec = 0.5, ceil = 1 agent per hour
        for hour in range(8, 12):
            self.assertEqual(self.scheduler.schedule[hour].total_agents, 1)
            self.assertEqual(self.scheduler.schedule[hour].breakdown["Customer B"], 1)

    def test_schedule_requirement_with_reduced_utilization(self):
        """Test scheduling with reduced utilization (agents work less efficiently)"""
        scheduler = Scheduler(utilization=0.8)
        req = CallRequirement(
            customer_name="Customer C",
            avg_duration_sec=600,
            start_hour=9,
            end_hour=10,
            total_calls=6,
            priority=1
        )
        scheduler.process_requirements([req])
        
        # 6 calls/hour * 600 sec/call / (3600 * 0.8) = 1.25, ceil = 2 agents
        self.assertEqual(scheduler.schedule[9].total_agents, 2)

    def test_schedule_requirement_high_volume(self):
        """Test scheduling a high-volume requirement"""
        req = CallRequirement(
            customer_name="Customer D",
            avg_duration_sec=1200,  # 20 minutes
            start_hour=9,
            end_hour=10,
            total_calls=18,  # 18 calls in 1 hour
            priority=1
        )
        self.scheduler.process_requirements([req])
        
        # 18 calls/hour * 1200 sec/call / 3600 sec = 6 agents
        self.assertEqual(self.scheduler.schedule[9].total_agents, 6)

    def test_schedule_multiple_requirements_same_hour(self):
        """Test scheduling multiple requirements that overlap in same hour"""
        req1 = CallRequirement(
            customer_name="Customer A",
            avg_duration_sec=600,
            start_hour=10,
            end_hour=11,
            total_calls=6,
            priority=1
        )
        req2 = CallRequirement(
            customer_name="Customer B",
            avg_duration_sec=300,
            start_hour=10,
            end_hour=11,
            total_calls=12,
            priority=2
        )
        self.scheduler.process_requirements([req1, req2])
        
        # req1: 6 * 600 / 3600 = 1 agent
        # req2: 12 * 300 / 3600 = 1 agent
        # total: 2 agents
        self.assertEqual(self.scheduler.schedule[10].total_agents, 2)
        self.assertEqual(self.scheduler.schedule[10].breakdown["Customer A"], 1)
        self.assertEqual(self.scheduler.schedule[10].breakdown["Customer B"], 1)

    def test_schedule_multiple_requirements_different_hours(self):
        """Test scheduling multiple requirements with different time ranges"""
        req1 = CallRequirement(
            customer_name="Customer A",
            avg_duration_sec=600,
            start_hour=9,
            end_hour=11,
            total_calls=12,
            priority=1
        )
        req2 = CallRequirement(
            customer_name="Customer B",
            avg_duration_sec=300,
            start_hour=11,
            end_hour=13,
            total_calls=12,
            priority=2
        )
        self.scheduler.process_requirements([req1, req2])
        
        # Hour 9-10: only Customer A
        self.assertEqual(self.scheduler.schedule[9].total_agents, 1)
        self.assertEqual(self.scheduler.schedule[9].breakdown["Customer A"], 1)
        
        # Hour 10-11: only Customer A (req1 ends at 11, exclusive)
        self.assertEqual(self.scheduler.schedule[10].total_agents, 1)
        
        # Hour 11-12: only Customer B
        self.assertEqual(self.scheduler.schedule[11].total_agents, 1)
        self.assertEqual(self.scheduler.schedule[11].breakdown["Customer B"], 1)

    def test_schedule_requirement_ceiling_calculation(self):
        """Test that agent count is correctly ceiled"""
        # Create a scenario where workload requires fractional agents
        req = CallRequirement(
            customer_name="Customer E",
            avg_duration_sec=1000,
            start_hour=9,
            end_hour=10,
            total_calls=3,  # 3 calls/hour * 1000 sec = 3000 sec, 3000/3600 = 0.833
            priority=1
        )
        self.scheduler.process_requirements([req])
        
        # Should be ceiled to 1 agent
        self.assertEqual(self.scheduler.schedule[9].total_agents, 1)

    def test_schedule_requirement_utilization_protection(self):
        """Test that utilization is protected from being too low"""
        # Even with 0 utilization passed, it should use at least 0.01
        scheduler = Scheduler(utilization=0.0)
        req = CallRequirement(
            customer_name="Customer F",
            avg_duration_sec=600,
            start_hour=9,
            end_hour=10,
            total_calls=6,
            priority=1
        )
        scheduler.process_requirements([req])
        
        # Should still work without division by zero
        # With util_factor = 0.01: 6 * 600 / (3600 * 0.01) = 100 agents
        self.assertEqual(scheduler.schedule[9].total_agents, 100)

    def test_schedule_requirement_all_day(self):
        """Test scheduling a requirement that spans the entire day"""
        req = CallRequirement(
            customer_name="Customer G",
            avg_duration_sec=600,
            start_hour=0,
            end_hour=24,
            total_calls=1,  # 6 calls per hour
            priority=1
        )
        self.scheduler.process_requirements([req])
        
        # Each hour should have 1 agent
        for hour in range(24):
            self.assertEqual(self.scheduler.schedule[hour].total_agents, 1)
            self.assertEqual(self.scheduler.schedule[hour].breakdown["Customer G"], 1)

    def test_schedule_requirement_breakdown_accuracy(self):
        """Test that breakdown dictionary correctly tracks customer agents"""
        req = CallRequirement(
            customer_name="Customer H",
            avg_duration_sec=600,
            start_hour=9,
            end_hour=12,
            total_calls=18,
            priority=3
        )
        self.scheduler.process_requirements([req])
        
        # Each hour should have Customer H in breakdown
        for hour in range(9, 12):
            self.assertIn("Customer H", self.scheduler.schedule[hour].breakdown)
            self.assertEqual(self.scheduler.schedule[hour].breakdown["Customer H"], 1)

    def test_schedule_empty_requirements(self):
        """Test processing empty requirements list"""
        self.scheduler.process_requirements([])
        
        # All buckets should remain unchanged
        for bucket in self.scheduler.schedule:
            self.assertEqual(bucket.total_agents, 0)
            self.assertEqual(bucket.breakdown, {})

    def test_schedule_requirement_calls_per_hour_calculation(self):
        """Test that calls_per_hour is correctly used in calculation"""
        # CallRequirement with 10 hour span and 100 total calls = 10 calls per hour
        req = CallRequirement(
            customer_name="Customer I",
            avg_duration_sec=180,  # 3 minutes
            start_hour=8,
            end_hour=18,
            total_calls=100,
            priority=1
        )
        self.scheduler.process_requirements([req])
        
        # 10 calls/hour * 180 sec/call / 3600 sec = 0.5, ceil = 1 agent per hour
        for hour in range(8, 18):
            self.assertEqual(self.scheduler.schedule[hour].total_agents, 1)

    def test_schedule_requirement_very_short_calls(self):
        """Test scheduling requirement with very short call duration"""
        req = CallRequirement(
            customer_name="Customer J",
            avg_duration_sec=30,  # 30 seconds
            start_hour=9,
            end_hour=10,
            total_calls=100,  # 100 calls in 1 hour
            priority=1
        )
        self.scheduler.process_requirements([req])
        
        # 100 calls/hour * 30 sec/call / 3600 sec = 0.833, ceil = 1 agent
        self.assertEqual(self.scheduler.schedule[9].total_agents, 1)

    def test_schedule_requirement_very_long_calls(self):
        """Test scheduling requirement with very long call duration"""
        req = CallRequirement(
            customer_name="Customer K",
            avg_duration_sec=3600,  # 1 hour
            start_hour=9,
            end_hour=10,
            total_calls=2,
            priority=1
        )
        self.scheduler.process_requirements([req])
        
        # 2 calls/hour * 3600 sec/call / 3600 sec = 2 agents
        self.assertEqual(self.scheduler.schedule[9].total_agents, 2)


if __name__ == '__main__':
    unittest.main()
