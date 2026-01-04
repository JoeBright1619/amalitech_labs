from collections import Counter, defaultdict, deque
from typing import Dict, List

from .models import Grade, Student, StudentList


def group_students_by_major(students: StudentList) -> Dict[str, List[Student]]:
    """Groups students by their major using defaultdict."""
    grouped = defaultdict(list)
    for student in students:
        grouped[student.major].append(student)
    return dict(grouped)


def count_grade_distribution(grades: List[Grade]) -> Counter:
    """Counts the distribution of grade letters using Counter."""
    return Counter(grade.grade_letter for grade in grades)


class RollingAverageCalculator:
    """Uses a deque to maintain a rolling average of the last N scores."""

    def __init__(self, window_size: int = 5):
        self.scores = deque(maxlen=window_size)

    def add_score(self, score: float) -> None:
        self.scores.append(score)

    @property
    def average(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores) / len(self.scores)
