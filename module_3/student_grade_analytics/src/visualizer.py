import matplotlib.pyplot as plt
from typing import Dict
from pathlib import Path


class Visualizer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_grade_distribution(self, distribution: Dict[str, int]):
        """Generates a bar chart for grade distribution."""
        grades = list(distribution.keys())
        counts = list(distribution.values())

        plt.figure(figsize=(10, 6))
        plt.bar(grades, counts, color="skyblue")
        plt.title("Grade Distribution")
        plt.xlabel("Grade")
        plt.ylabel("Number of Students")

        output_path = self.output_dir / "grade_distribution.png"
        plt.savefig(output_path)
        plt.close()
        print(f"Grade distribution chart saved to {output_path}")

    def plot_major_distribution(self, distribution: Dict[str, int]):
        """Generates a pie chart for major distribution."""
        majors = list(distribution.keys())
        counts = list(distribution.values())

        plt.figure(figsize=(8, 8))
        plt.pie(
            counts,
            labels=majors,
            autopct="%1.1f%%",
            startangle=140,
            colors=["gold", "lightcoral", "lightskyblue", "lightgreen"],
        )
        plt.title("Student Distribution by Major")

        output_path = self.output_dir / "major_distribution.png"
        plt.savefig(output_path)
        plt.close()
        print(f"Major distribution chart saved to {output_path}")
