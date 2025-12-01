import unittest
import tempfile
import os
from pathlib import Path
from typing import List
from src.parser import InputParser
from src.models import CallRequirement


class TestInputParser(unittest.TestCase):
    """Unit tests for the InputParser class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name

    def tearDown(self):
        """Clean up temporary files"""
        self.temp_dir.cleanup()

    def _create_csv(self, filename: str, content: str) -> str:
        """Helper method to create a temporary CSV file"""
        filepath = os.path.join(self.temp_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath

    # Tests for extract_hour method
    def test_extract_hour_valid_time_24h_format(self):
        """Test extracting hour from 24-hour format time string"""
        self.assertEqual(InputParser.extract_hour("14:30"), 14)
        self.assertEqual(InputParser.extract_hour("09:15"), 9)
        self.assertEqual(InputParser.extract_hour("00:00"), 0)
        self.assertEqual(InputParser.extract_hour("23:59"), 23)

    def test_extract_hour_valid_time_12h_format(self):
        """Test extracting hour from 12-hour format time string"""
        self.assertEqual(InputParser.extract_hour("2:30 PM"), 14)
        self.assertEqual(InputParser.extract_hour("9:15 AM"), 9)
        self.assertEqual(InputParser.extract_hour("12:00 PM"), 12)
        self.assertEqual(InputParser.extract_hour("12:00 AM"), 0)
        self.assertEqual(InputParser.extract_hour("1:00 am"), 1)
        self.assertEqual(InputParser.extract_hour("1Pm"), 13)
        self.assertEqual(InputParser.extract_hour("11:00 Am"), 11)

    def test_extract_hour_various_formats(self):
        """Test that extract_hour can handle various datetime formats"""
        self.assertEqual(InputParser.extract_hour("2024-11-30 15:45"), 15)
        self.assertEqual(InputParser.extract_hour("15:45:30"), 15)

    def test_extract_hour_invalid_format(self):
        """Test that extract_hour raises ValueError for invalid formats"""
        with self.assertRaises(ValueError):
            InputParser.extract_hour("invalid time")
        with self.assertRaises(ValueError):
            InputParser.extract_hour("25:00")
        with self.assertRaises(ValueError):
            InputParser.extract_hour("")
        with self.assertRaises(ValueError):
            InputParser.extract_hour("25")

    # Tests for validate_columns method
    def test_validate_columns_valid_header(self):
        """Test validation passes for correct header"""
        header = ['CustomerName', 'AverageCallDurationSeconds', 'StartTimePT', 'EndTimePT', 'NumberOfCalls', 'Priority']
        # Should not raise an exception
        InputParser.validate_columns(header)

    def test_validate_columns_missing_header(self):
        """Test validation fails when header is None"""
        with self.assertRaises(ValueError) as context:
            InputParser.validate_columns(None)
        self.assertIn("missing a header row", str(context.exception))

    def test_validate_columns_wrong_column_name(self):
        """Test validation fails for incorrect column names"""
        header = ['Name', 'AverageCallDurationSeconds', 'StartTimePT', 'EndTimePT', 'NumberOfCalls', 'Priority']
        with self.assertRaises(ValueError) as context:
            InputParser.validate_columns(header)
        self.assertIn("CustomerName", str(context.exception))

    def test_validate_columns_missing_columns(self):
        """Test validation fails when columns are missing"""
        header = ['CustomerName', 'AverageCallDurationSeconds', 'StartTimePT']
        with self.assertRaises(ValueError):
            InputParser.validate_columns(header)

    def test_validate_columns_extra_whitespace(self):
        """Test that column names with extra whitespace fail validation"""
        header = ['CustomerName ', 'AverageCallDurationSeconds', 'StartTimePT', 'EndTimePT', 'NumberOfCalls', 'Priority']
        # should not raise an exception
        InputParser.validate_columns(header)

    # Tests for parse_csv method
    def test_parse_csv_valid_file(self):
        """Test parsing a valid CSV file"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        John Doe,300,09:00,17:00,50,1
                        Jane Smith,600,10:00,18:00,30,2
                        """
        filepath = self._create_csv("valid.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        self.assertEqual(len(requirements), 2)
        self.assertEqual(requirements[0].customer_name, "John Doe")
        self.assertEqual(requirements[0].avg_duration_sec, 300)
        self.assertEqual(requirements[0].start_hour, 9)
        self.assertEqual(requirements[0].end_hour, 17)
        self.assertEqual(requirements[0].total_calls, 50)
        self.assertEqual(requirements[0].priority, 1)

    def test_parse_csv_with_spaces_in_data(self):
        """Test that leading/trailing spaces are trimmed from data"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        Bob White , 500 , 09:30 , 17:30 , 40 , 2
                        """
        filepath = self._create_csv("spaces.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].customer_name, "Bob White")
        self.assertEqual(requirements[0].avg_duration_sec, 500)
        self.assertEqual(requirements[0].start_hour, 9)
        self.assertEqual(requirements[0].end_hour, 17)
        self.assertEqual(requirements[0].total_calls, 40)
        self.assertEqual(requirements[0].priority, 2)

    def test_parse_csv_file_not_found(self):
        """Test that FileNotFoundError is handled gracefully"""
        with self.assertRaises(SystemExit):
            InputParser.parse_csv("/nonexistent/path/file.csv")

    def test_parse_csv_invalid_duration(self):
        """Test that invalid duration value is skipped"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        John Doe,invalid,09:00,17:00,50,1
                        Jane Smith,600,10:00,18:00,30,2
                        """
        filepath = self._create_csv("invalid_duration.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        # First row should be skipped, second row should be parsed
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].customer_name, "Jane Smith")

    def test_parse_csv_invalid_hour(self):
        """Test that invalid hour in time string is skipped"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        John Doe,300,16161,17:00,50,1
                        Jane Smith,600,10:00,18:00,30,2
                        """
        filepath = self._create_csv("invalid_hour.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        # First row should be skipped, second row should be parsed
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].customer_name, "Jane Smith")

    def test_parse_csv_invalid_calls_count(self):
        """Test that invalid calls count is skipped"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        John Doe,300,09:00,17:00,-1,1
                        Jane Smith,600,10:00,18:00,30,2
                        """
        filepath = self._create_csv("invalid_calls.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        # First row should be skipped, second row should be parsed
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].customer_name, "Jane Smith")

    def test_parse_csv_invalid_priority(self):
        """Test that invalid priority value is skipped"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        John Doe,300,09:00,17:00,50,10
                        Jane Smith,600,10:00,18:00,30,2
                        """
        filepath = self._create_csv("invalid_priority.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        # First row should be skipped due to invalid priority, second row should be parsed
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].customer_name, "Jane Smith")

    def test_parse_csv_incomplete_row(self):
        """Test that incomplete rows are skipped"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        John Doe,300,09:00,17:00
                        Jane Smith,600,10:00,18:00,30,2
                        """
        filepath = self._create_csv("incomplete.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        # First row should be skipped, second row should be parsed
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].customer_name, "Jane Smith")

    def test_parse_csv_empty_rows(self):
        """Test that empty rows are skipped"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        John Doe,300,09:00,17:00,50,1

                        Jane Smith,600,10:00,18:00,30,2
                        """
        filepath = self._create_csv("empty_rows.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        # Both valid rows should be parsed
        self.assertEqual(len(requirements), 2)
        self.assertEqual(requirements[0].customer_name, "John Doe")
        self.assertEqual(requirements[1].customer_name, "Jane Smith")

    def test_parse_csv_returns_call_requirement_objects(self):
        """Test that parse_csv returns CallRequirement objects"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        John Doe,300,09:00,17:00,50,1
                        """
        filepath = self._create_csv("valid.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        self.assertEqual(len(requirements), 1)
        self.assertIsInstance(requirements[0], CallRequirement)

    def test_parse_csv_various_time_formats(self):
        """Test parsing CSV with various time formats"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        John Doe,300,9:00 AM,5:00 PM,50,1
                        Jane Smith,600,10:00,18:00,30,2
                        """
        filepath = self._create_csv("mixed_formats.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        self.assertEqual(len(requirements), 2)
        self.assertEqual(requirements[0].start_hour, 9)
        self.assertEqual(requirements[0].end_hour, 17)


    def test_parse_csv_start_hour_greater_than_end_hour(self):
        """Test that start hour greater than end hour raises ValueError"""
        csv_content = """CustomerName,AverageCallDurationSeconds,StartTimePT,EndTimePT,NumberOfCalls,Priority
                        John Doe,300,18:00,09:00,50,1
                        Jane Smith,600,10:00,18:00,30,2
                        """
        filepath = self._create_csv("invalid_hours.csv", csv_content)
        
        requirements = InputParser.parse_csv(filepath)
        
        # The row should be skipped due to invalid hours
        self.assertEqual(requirements[0].customer_name, "Jane Smith")



if __name__ == '__main__':
    unittest.main()
