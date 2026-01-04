from src.models import Student, Grade
from src.collections_util import RollingAverageCalculator, group_students_by_major


def test_student_gpa():
    student = Student("S1", "Test", "CS", 1)
    student.add_grade(Grade("S1", "C1", 80.0, "B"))
    student.add_grade(Grade("S1", "C2", 90.0, "A"))
    assert student.gpa == 85.0


def test_rolling_average():
    roller = RollingAverageCalculator(window_size=3)
    roller.add_score(10)
    roller.add_score(20)
    roller.add_score(30)
    assert roller.average == 20.0
    roller.add_score(40)
    assert roller.average == 30.0  # (20+30+40)/3


def test_group_by_major():
    students = [
        Student("S1", "A", "CS", 1),
        Student("S2", "B", "Math", 2),
        Student("S3", "C", "CS", 3),
    ]
    grouped = group_students_by_major(students)
    assert len(grouped["CS"]) == 2
    assert len(grouped["Math"]) == 1
