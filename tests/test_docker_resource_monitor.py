import unittest
from unittest.mock import patch, Mock

from scripts.docker_resource_monitor import (
    parse_stats,
    collect_stats,
)


class DockerResourceMonitorTests(unittest.TestCase):

    def test_parse_single_container(self):
        output = (
            '{"Name":"infrasentry-backend",'
            '"CPUPerc":"2.50%",'
            '"MemUsage":"300MiB / 2GiB",'
            '"MemPerc":"15.00%",'
            '"NetIO":"1kB / 2kB",'
            '"BlockIO":"3kB / 4kB",'
            '"PIDs":"12"}'
        )

        records = parse_stats(output)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "infrasentry-backend")
        self.assertEqual(records[0]["cpu"], "2.50%")
        self.assertEqual(records[0]["pids"], "12")

    def test_parse_multiple_containers(self):
        output = (
            '{"Name":"frontend","CPUPerc":"1%"}\n'
            '{"Name":"backend","CPUPerc":"2%"}\n'
        )

        records = parse_stats(output)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[1]["name"], "backend")

    def test_empty_output(self):
        self.assertEqual(parse_stats(""), [])

    def test_invalid_json(self):
        with self.assertRaises(ValueError):
            parse_stats("not-json")

    @patch("scripts.docker_resource_monitor.subprocess.run")
    def test_collect_stats_success(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"Name":"backend","CPUPerc":"2%"}',
            stderr="",
        )

        records = collect_stats()

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "backend")

    @patch("scripts.docker_resource_monitor.subprocess.run")
    def test_collect_stats_failure(self, mock_run):
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Docker daemon unavailable",
        )

        with self.assertRaises(RuntimeError):
            collect_stats()


if __name__ == "__main__":
    unittest.main()
