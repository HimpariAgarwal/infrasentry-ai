import json
import subprocess
import sys


def parse_stats(output: str) -> list[dict]:
    records = []

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        item = json.loads(line)
        records.append({
            "name": item.get("Name") or item.get("Container", "unknown"),
            "cpu": item.get("CPUPerc", "N/A"),
            "memory": item.get("MemUsage", "N/A"),
            "memory_percent": item.get("MemPerc", "N/A"),
            "network": item.get("NetIO", "N/A"),
            "block_io": item.get("BlockIO", "N/A"),
            "pids": item.get("PIDs", "N/A"),
        })

    return records


def collect_stats() -> list[dict]:
    result = subprocess.run(
        [
            "docker", "stats", "--no-stream",
            "--format", "{{json .}}",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Docker stats failed")

    return parse_stats(result.stdout)


def print_report(records: list[dict]) -> None:
    print("\nInfraSentry AI - Docker Resource Report")
    print("=" * 72)

    if not records:
        print("No running containers found.")
        return

    for item in records:
        print(f"\nContainer: {item['name']}")
        print(f"  CPU:           {item['cpu']}")
        print(f"  Memory:        {item['memory']}")
        print(f"  Memory usage:  {item['memory_percent']}")
        print(f"  Network I/O:   {item['network']}")
        print(f"  Block I/O:     {item['block_io']}")
        print(f"  Processes:     {item['pids']}")

    print("\n" + "=" * 72)
    print(f"Total containers monitored: {len(records)}")


def main() -> int:
    try:
        records = collect_stats()
        print_report(records)
        return 0
    except (RuntimeError, OSError, subprocess.TimeoutExpired,
            json.JSONDecodeError) as error:
        print(f"Resource monitoring failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
