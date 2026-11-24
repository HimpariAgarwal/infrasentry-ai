import argparse
import sys
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


@dataclass
class HealthResult:
    name: str
    url: str
    healthy: bool
    status_code: int | None
    detail: str


def check_endpoint(name: str, url: str, timeout: int = 5) -> HealthResult:
    try:
        with urlopen(url, timeout=timeout) as response:
            status = response.status
            return HealthResult(
                name, url, status == 200, status,
                "HTTP response received"
            )
    except HTTPError as error:
        return HealthResult(
            name, url, False, error.code,
            f"HTTP error: {error.reason}"
        )
    except URLError as error:
        return HealthResult(
            name, url, False, None,
            f"Connection error: {error.reason}"
        )
    except Exception as error:
        return HealthResult(
            name, url, False, None,
            f"{type(error).__name__}: {error}"
        )


def run_checks(
    frontend_url: str = "http://localhost:3000/health",
    backend_url: str = "http://localhost:8000/health",
    timeout: int = 5,
) -> bool:
    results = [
        check_endpoint("Frontend", frontend_url, timeout),
        check_endpoint("Backend", backend_url, timeout),
    ]

    print("\nInfraSentry AI - Production Health Report")
    print("=" * 52)

    for result in results:
        state = "HEALTHY" if result.healthy else "UNHEALTHY"
        status = (
            str(result.status_code)
            if result.status_code is not None
            else "N/A"
        )
        print(f"{result.name}: {state}")
        print(f"  URL: {result.url}")
        print(f"  HTTP: {status}")
        print(f"  Detail: {result.detail}")

    all_healthy = all(result.healthy for result in results)

    print("=" * 52)
    print("OVERALL:", "HEALTHY" if all_healthy else "DEGRADED")

    return all_healthy


def main() -> int:
    parser = argparse.ArgumentParser(
        description="InfraSentry AI production health monitor"
    )
    parser.add_argument(
        "--frontend",
        default="http://localhost:3000/health",
        help="Frontend health endpoint",
    )
    parser.add_argument(
        "--backend",
        default="http://localhost:8000/health",
        help="Backend health endpoint",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Request timeout in seconds",
    )

    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    return 0 if run_checks(
        args.frontend, args.backend, args.timeout
    ) else 1


if __name__ == "__main__":
    sys.exit(main())
