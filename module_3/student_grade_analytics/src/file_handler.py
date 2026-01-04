import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

from .models import Grade, Student


class FileHandler:
    @staticmethod
    def load_students_from_csv(file_path: Union[str, Path]) -> List[Student]:
        """Reads student basic info from a CSV file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Student CSV file not found: {file_path}")

        students = []
        try:
            with path.open(mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    student = Student(
                        student_id=row["student_id"],
                        name=row["name"],
                        major=row["major"],
                        year=int(row["year"]),
                    )
                    students.append(student)
        except Exception as e:
            print(f"Error reading students CSV: {e}")
            raise
        return students

    @staticmethod
    def load_grades_from_csv(file_path: Union[str, Path]) -> List[Grade]:
        """Reads grades from a CSV file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Grades CSV file not found: {file_path}")

        grades = []
        try:
            with path.open(mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    grade = Grade(
                        student_id=row["student_id"],
                        course_id=row["course_id"],
                        score=float(row["score"]),
                        grade_letter=row["grade_letter"],
                        timestamp=(
                            datetime.fromisoformat(row["timestamp"])
                            if "timestamp" in row
                            else datetime.now()
                        ),
                    )
                    grades.append(grade)
        except Exception as e:
            print(f"Error reading grades CSV: {e}")
            raise
        return grades

    @staticmethod
    def save_report_to_json(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
        """Writes the analytics report to a JSON file."""
        path = Path(file_path)
        try:
            # Ensure parent directories exist
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open(mode="w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except PermissionError:
            print(f"Permission denied: Unable to write to {file_path}")
            raise
        except Exception as e:
            print(f"Error saving JSON report: {e}")
            raise
