# Day 114 - Docker Resource Monitoring

## Objective
Monitor resource consumption of running Docker containers.

## Metrics
- CPU percentage
- Memory usage and percentage
- Network input/output
- Block I/O
- Process count

## Run

From the project root:

```powershell
python scripts/docker_resource_monitor.py
```

The Docker daemon must be running.

## Tests

```powershell
python -m unittest discover -s tests -p "test_docker_resource_monitor.py" -v
```

## Limitations
This tool reports a point-in-time Docker resource snapshot.
It does not calculate historical trends, enforce resource limits,
or automatically restart containers.
