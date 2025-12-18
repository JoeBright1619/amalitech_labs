from pathlib import Path
import subprocess
import sys


def test_cli_runs_successfully(tmp_path: Path):
    csv_file = tmp_path / "users.csv"
    csv_file.write_text("user_id,name,email\n1,Bright,bright@test.com\n")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "module_2.resilient_data_importer_cli.cli",
            "--db",
            str(tmp_path / "db.json"),
            str(csv_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Successfully imported 1 users" in result.stdout
