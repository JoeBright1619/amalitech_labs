import statistics
from collections import Counter, OrderedDict
from typing import Any, Dict, List, TypedDict

from .collections_util import RollingAverageCalculator, count_grade_distribution
from .models import Student


class ReportStructure(TypedDict):
    total_students: int
    overall_average: float
    gpa_statistics: Dict[str, float]
    grade_distribution: Dict[str, int]
    major_distribution: Dict[str, int]
    top_performers: List[Dict[str, Any]]
    percentile_rankings: Dict[str, float]
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

    def get_gpa_statistics(self) -> Dict[str, float]:
        """Calculates Mean, Median, and Mode of GPAs."""
        gpas = [round(s.gpa, 2) for s in self.students if s.grades]
        if not gpas:
            return {"mean": 0.0, "median": 0.0, "mode": 0.0}

        return {
            "mean": round(statistics.mean(gpas), 2),
            "median": round(statistics.median(gpas), 2),
            "mode": round(statistics.mode(gpas), 2),
        }

    def calculate_percentiles(self) -> Dict[str, float]:
        """Calculates the percentile ranking for each student based on GPA."""
        gpas = [s.gpa for s in self.students if s.grades]
        if not gpas:
            return {}

        gpas.sort()
        n = len(gpas)
        percentiles = {}

        for student in self.students:
            if not student.grades:
                percentiles[student.student_id] = 0.0
                continue

            # Simple percentile rank: (count of scores < score) / total_scores * 100
            # Or using scipy's style, strictly simpler here:
            rank = sum(1 for g in gpas if g < student.gpa)
            percentile = (rank / n) * 100
            percentiles[student.student_id] = round(percentile, 2)

        return percentiles

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
                ("gpa_statistics", self.get_gpa_statistics()),
                ("grade_distribution", dict(count_grade_distribution(all_grades))),
                ("major_distribution", self.get_major_distribution()),
                ("top_performers", self.get_top_performers()),
                ("percentile_rankings", self.calculate_percentiles()),
                (
                    "rolling_averages_trend",
                    rolling_history[-10:] if rolling_history else [],
                ),
            ]
        )

        return report
