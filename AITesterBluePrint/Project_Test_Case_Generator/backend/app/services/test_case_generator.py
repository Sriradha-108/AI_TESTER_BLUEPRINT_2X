"""Test case generation orchestration service"""
import logging
from typing import Dict, List
import csv
import io
from datetime import datetime

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting test cases in different formats"""
    
    @staticmethod
    def export_to_csv(test_cases: List[Dict]) -> str:
        """
        Export test cases to CSV format.
        
        Args:
            test_cases: List of test case dictionaries
            
        Returns:
            CSV string
        """
        if not test_cases:
            return ""
        
        output = io.StringIO()
        fieldnames = [
            "ID", "Title", "Type", "Priority", "Preconditions",
            "Steps", "Test Data", "Expected Result", "Linked Jira ID"
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for tc in test_cases:
            writer.writerow({
                "ID": tc.get("id", ""),
                "Title": tc.get("title", ""),
                "Type": tc.get("type", ""),
                "Priority": tc.get("priority", ""),
                "Preconditions": tc.get("preconditions", ""),
                "Steps": "; ".join(tc.get("steps", [])),
                "Test Data": tc.get("test_data", ""),
                "Expected Result": tc.get("expected_result", ""),
                "Linked Jira ID": tc.get("linked_jira_id", ""),
            })
        
        return output.getvalue()
    
    @staticmethod
    def export_to_tsv(test_cases: List[Dict]) -> str:
        """
        Export test cases to TSV (Tab-Separated Values) format for Jira/Xray.
        
        Args:
            test_cases: List of test case dictionaries
            
        Returns:
            TSV string
        """
        if not test_cases:
            return ""
        
        output = io.StringIO()
        fieldnames = [
            "ID", "Title", "Type", "Priority", "Preconditions",
            "Steps", "Test Data", "Expected Result", "Linked Jira ID"
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        
        for tc in test_cases:
            writer.writerow({
                "ID": tc.get("id", ""),
                "Title": tc.get("title", ""),
                "Type": tc.get("type", ""),
                "Priority": tc.get("priority", ""),
                "Preconditions": tc.get("preconditions", ""),
                "Steps": "\n".join(tc.get("steps", [])),
                "Test Data": tc.get("test_data", ""),
                "Expected Result": tc.get("expected_result", ""),
                "Linked Jira ID": tc.get("linked_jira_id", ""),
            })
        
        return output.getvalue()
    
    @staticmethod
    def export_to_markdown(test_cases: List[Dict], jira_id: str = "") -> str:
        """
        Export test cases to Markdown format.
        
        Args:
            test_cases: List of test case dictionaries
            jira_id: Jira issue ID for reference
            
        Returns:
            Markdown string
        """
        if not test_cases:
            return ""
        
        md = f"# Test Cases\n\n"
        if jira_id:
            md += f"**Linked Jira Issue:** {jira_id}\n\n"
        md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Total Test Cases:** {len(test_cases)}\n\n"
        
        for i, tc in enumerate(test_cases, 1):
            md += f"## {i}. {tc.get('title', 'Test Case')}\n\n"
            md += f"| Attribute | Value |\n"
            md += f"|-----------|-------|\n"
            md += f"| ID | `{tc.get('id', '')}` |\n"
            md += f"| Type | {tc.get('type', '')} |\n"
            md += f"| Priority | {tc.get('priority', '')} |\n"
            md += f"| Preconditions | {tc.get('preconditions', 'None')} |\n"
            
            steps = tc.get("steps", [])
            steps_text = "\n".join([f"{j}. {step}" for j, step in enumerate(steps, 1)])
            md += f"| Steps | {steps_text} |\n"
            
            md += f"| Test Data | {tc.get('test_data', 'N/A')} |\n"
            md += f"| Expected Result | {tc.get('expected_result', '')} |\n"
            md += f"| Linked Jira ID | {tc.get('linked_jira_id', '')} |\n\n"
        
        return md


class TestCaseValidator:
    """Service to validate generated test cases"""
    
    @staticmethod
    def validate_test_case(tc: Dict) -> bool:
        """
        Validate a single test case structure.
        
        Args:
            tc: Test case dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["id", "title", "type", "priority", "steps", "expected_result"]
        
        for field in required_fields:
            if field not in tc or not tc[field]:
                logger.warning(f"Test case missing required field: {field}")
                return False
        
        # Validate type
        valid_types = ["Positive", "Negative", "Edge", "Boundary", "Security"]
        if tc["type"] not in valid_types:
            logger.warning(f"Invalid test case type: {tc['type']}")
            return False
        
        # Validate priority
        valid_priorities = ["P0", "P1", "P2"]
        if tc["priority"] not in valid_priorities:
            logger.warning(f"Invalid priority: {tc['priority']}")
            return False
        
        # Validate steps is a list
        if not isinstance(tc["steps"], list) or len(tc["steps"]) == 0:
            logger.warning("steps must be a non-empty list")
            return False
        
        return True
    
    @staticmethod
    def validate_test_cases(test_cases: List[Dict], min_cases: int = 5) -> tuple[bool, List[str]]:
        """
        Validate all test cases.
        
        Args:
            test_cases: List of test cases
            min_cases: Minimum number of test cases required
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if len(test_cases) < min_cases:
            errors.append(f"Expected at least {min_cases} test cases, got {len(test_cases)}")
        
        for i, tc in enumerate(test_cases):
            if not TestCaseValidator.validate_test_case(tc):
                errors.append(f"Test case {i} (ID: {tc.get('id', 'unknown')}) is invalid")
        
        return len(errors) == 0, errors
