import random
from datetime import datetime, timedelta


def generate_logs(file_path: str, num_lines: int = 1000):
    ips = ["192.168.1.1", "10.0.0.5", "172.16.0.10", "127.0.0.1", "8.8.8.8"]
    methods = ["GET", "POST", "PUT", "DELETE"]
    urls = [
        "/index.html",
        "/api/v1/users",
        "/login",
        "/products?id=123",
        "/images/logo.png",
    ]
    statuses = [200, 201, 304, 400, 404, 500]
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKitt/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Python-urllib/3.11",
    ]

    start_time = datetime(2023, 1, 1, 10, 0, 0)

    with open(file_path, "w", encoding="utf-8") as f:
        for i in range(num_lines):
            ip = random.choice(ips)
            ts = (start_time + timedelta(seconds=i)).strftime("%d/%b/%Y:%H:%M:%S +0000")
            method = random.choice(methods)
            url = random.choice(urls)
            status = random.choice(statuses)
            bytes_sent = random.randint(100, 5000)
            agent = random.choice(agents)

            line = f'{ip} - - [{ts}] "{method} {url} HTTP/1.1" {status} {bytes_sent} "http://referer.com" "{agent}"\n'
            f.write(line)


if __name__ == "__main__":
    from pathlib import Path

    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    generate_logs(str(data_dir / "access.log"), 5000)
    print(f"Generated 5000 log lines in {data_dir}/access.log")
