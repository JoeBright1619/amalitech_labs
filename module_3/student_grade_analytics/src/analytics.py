import statistics
from collections import Counter, OrderedDict
from typing import Any, Dict, List, TypedDict

from .collections_util import RollingAverageCalculator, count_grade_distribution
from .models import Student


class ReportStructure(TypedDict):
    total_students: int
    overall_average: float
    grade_distribution: Dict[str, int]
    major_distribution: Dict[str, int]
    top_performers: List[Dict[str, Any]]
    rolling_averages: List[float]


class GradeAnalyzer:
    def __init__(self, students: List[Student]):
        self.students = students

    def get_overall_average(self) -> float:
        """Calculates the average GPA across all students."""
        if not self.students:
            return 0.0
        gpas = [s.gpa for s in self.students if s.grades]
        return statistics.mean(gpas) if gpas else 0.0

    def get_major_distribution(self) -> Dict[str, int]:
        """Returns the number of students per major using Counter."""
        return dict(Counter(s.major for s in self.students))

    def get_top_performers(self, n: int = 3) -> List[Dict[str, Any]]:
        """Returns the top N students by GPA."""
        sorted_students = sorted(self.students, key=lambda s: s.gpa, reverse=True)
        return [
            {"name": s.name, "student_id": s.student_id, "gpa": round(s.gpa, 2)}
            for s in sorted_students[:n]
        ]

    def generate_full_report(self) -> OrderedDict:
        """Generates a comprehensive report in a specific order."""
        all_grades = []
        for s in self.students:
            all_grades.extend(s.grades)

        # Calculate rolling averages for the last 5 grade entries
        roller = RollingAverageCalculator(window_size=5)
        rolling_history = []
        for grade in all_grades:
            roller.add_score(grade.score)
            rolling_history.append(roller.average)

        report = OrderedDict(
            [
                ("total_students", len(self.students)),
                ("overall_average", round(self.get_overall_average(), 2)),
                ("grade_distribution", dict(count_grade_distribution(all_grades))),
                ("major_distribution", self.get_major_distribution()),
                ("top_performers", self.get_top_performers()),
                (
                    "rolling_averages_trend",
                    rolling_history[-10:] if rolling_history else [],
                ),
            ]
        )

        return report
