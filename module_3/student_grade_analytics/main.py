import sys
from pathlib import Path
from src.file_handler import FileHandler
from src.analytics import GradeAnalyzer
from src.visualizer import Visualizer


def main():
    # Define paths
    base_dir = Path(__file__).parent
    students_csv = base_dir / "data" / "students.csv"
    grades_csv = base_dir / "data" / "grades.csv"
    report_json = base_dir / "data" / "final_report.json"

    print("--- Student Grade Analytics Tool ---")

    try:
        # Load Data
        print(f"Loading data from {students_csv} and {grades_csv}...")
        students = FileHandler.load_students_from_csv(students_csv)
        grades = FileHandler.load_grades_from_csv(grades_csv)

        # Map grades to students
        student_map = {s.student_id: s for s in students}
        for grade in grades:
            if grade.student_id in student_map:
                student_map[grade.student_id].add_grade(grade)

        # Analyze Data
        print("Analyzing data...")
        analyzer = GradeAnalyzer(students)
        report = analyzer.generate_full_report()

        # Save Report
        print(f"Saving report to {report_json}...")
        FileHandler.save_report_to_json(report, report_json)

        # Generate Visualizations
        print("Generating visualizations...")
        visualizer = Visualizer(base_dir / "plots")
        visualizer.plot_grade_distribution(report["grade_distribution"])
        visualizer.plot_major_distribution(report["major_distribution"])

        # Visual Output
        print("\n--- Summary Report ---")
        print(f"Total Students: {report['total_students']}")
        print(f"Overall Average GPA: {report['overall_average']}")
        print("\nMajor Distribution:")
        for major, count in report["major_distribution"].items():
            print(f"  - {major}: {count}")

        print("\nTop Performers:")
        for performer in report["top_performers"]:
            print(f"  - {performer['name']} ({performer['gpa']})")

        print("\nProcess completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
