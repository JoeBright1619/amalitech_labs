from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, NamedTuple, Optional, Union


# Course as a NamedTuple for immutability and memory efficiency
class Course(NamedTuple):
    course_id: str
    course_name: str
    credits: int
    semester: str


# Grade as a Dataclass
@dataclass
class Grade:
    student_id: str
    course_id: str
    score: float
    grade_letter: str  # e.g., 'A', 'B', etc.
    timestamp: datetime = field(default_factory=datetime.now)


# Student as a Dataclass
@dataclass
class Student:
    student_id: str
    name: str
    major: str
    year: int
    grades: List[Grade] = field(default_factory=list)

    @property
    def gpa(self) -> float:
        if not self.grades:
            return 0.0
        return sum(g.score for g in self.grades) / len(self.grades)

    def add_grade(self, grade: Grade) -> None:
        """Adds a grade to the student's records."""
        self.grades.append(grade)


# Type Hints for complex structures
StudentList = List[Student]
GradeData = Dict[str, List[float]]
OptionalGrade = Optional[Grade]
InputData = Union[str, Dict]
