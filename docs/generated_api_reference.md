# InfraSentry AI - API Reference

Automatically generated static API route reference.

## Summary

- Python files scanned: 98
- Total routes discovered: 54
- Files containing routes: 21
- Duplicate candidates: 9
- Parsing errors: 0

## HTTP Method Distribution

| Method | Route Count |
|---|---:|
| DELETE | 3 |
| GET | 35 |
| PATCH | 3 |
| POST | 12 |
| PUT | 1 |

## Endpoints

| Method | Endpoint | Function | Source File |
|---|---|---|---|
| DELETE | `` | `clear_logs` | `logs_router.py` |
| GET | `` | `get_incidents` | `incident_router.py` |
| GET | `` | `get_logs` | `logs_router.py` |
| GET | `` | `list_retry_profiles` | `sla_scheduler_retry_profiles_router.py` |
| GET | `/` | `home` | `main.py` |
| GET | `/` | `get_retry_profile_comparison` | `sla_scheduler_retry_comparison_router.py` |
| GET | `/alerts` | `list_alerts` | `alerts_router.py` |
| GET | `/alerts` | `list_sla_alerts` | `sla_alerts_router.py` |
| POST | `/alerts/generate` | `generate_alerts` | `alerts_router.py` |
| POST | `/alerts/generate` | `create_sla_alerts` | `sla_alerts_router.py` |
| PATCH | `/alerts/{alert_id}/resolve` | `resolve_alert` | `alerts_router.py` |
| PATCH | `/alerts/{alert_id}/resolve` | `resolve_alert` | `sla_alerts_router.py` |
| GET | `/analytics` | `incident_analytics` | `incident_analytics_router.py` |
| GET | `/analytics/summary` | `analytics_summary` | `main.py` |
| GET | `/api/test` | `test_endpoint` | `test_security.py` |
| GET | `/api/v1/detect` | `protected_endpoint` | `test_api_access_control.py` |
| GET | `/api/v1/sla/retry-metrics` | `retry_metrics` | `sla_scheduler_retry_metrics_router.py` |
| GET | `/audit` | `get_security_audit` | `security_router.py` |
| GET | `/db-health` | `database_health` | `main.py` |
| POST | `/detect` | `detect_road_damage` | `ai_router.py` |
| GET | `/export` | `export_logs` | `logs_router.py` |
| POST | `/from-alerts` | `create_from_alerts` | `incident_router.py` |
| GET | `/health` | `health_check` | `main.py` |
| GET | `/health` | `public_endpoint` | `test_api_access_control.py` |
| GET | `/health` | `health_endpoint` | `test_security.py` |
| GET | `/history` | `detection_history` | `ai_router.py` |
| DELETE | `/history/{record_id}` | `remove_detection_history` | `ai_router.py` |
| GET | `/history/{record_id}` | `detection_history_detail` | `ai_router.py` |
| GET | `/images/processed` | `list_processed_images` | `image_upload.py` |
| GET | `/images/processed/{filename}` | `get_processed_image` | `image_upload.py` |
| POST | `/images/upload/{report_id}` | `upload_image` | `image_upload.py` |
| GET | `/me` | `get_profile` | `auth_router.py` |
| GET | `/model-info` | `model_info` | `ai_router.py` |
| GET | `/report` | `get_sla_report` | `sla_router.py` |
| GET | `/reports` | `get_reports` | `main.py` |
| POST | `/reports` | `create_report` | `main.py` |
| GET | `/reports/severity/{severity}` | `get_reports_by_severity` | `main.py` |
| DELETE | `/reports/{report_id}` | `delete_report` | `main.py` |
| GET | `/reports/{report_id}` | `get_report` | `main.py` |
| PUT | `/reports/{report_id}` | `update_report` | `main.py` |
| GET | `/scheduler-analytics` | `scheduler_analytics` | `sla_scheduler_analytics_router.py` |
| GET | `/scheduler-status` | `scheduler_status` | `sla_scheduler_router.py` |
| POST | `/scheduler/pause` | `scheduler_pause` | `sla_scheduler_router.py` |
| POST | `/scheduler/resume` | `scheduler_resume` | `sla_scheduler_router.py` |
| POST | `/scheduler/start` | `scheduler_start` | `sla_scheduler_router.py` |
| POST | `/scheduler/stop` | `scheduler_stop` | `sla_scheduler_router.py` |
| POST | `/scheduler/trigger` | `scheduler_trigger` | `sla_scheduler_router.py` |
| GET | `/secure-check` | `secure_check` | `auth_router.py` |
| GET | `/system-health` | `system_health` | `system_router.py` |
| GET | `/threat-analysis` | `threat_analysis` | `threat_router.py` |
| POST | `/token` | `login` | `auth_router.py` |
| PATCH | `/{incident_id}` | `patch_incident` | `incident_router.py` |
| GET | `/{profile_name}` | `get_retry_profile_preview` | `sla_scheduler_retry_preview_router.py` |
| GET | `/{profile_name}` | `read_retry_profile` | `sla_scheduler_retry_profiles_router.py` |

## Duplicate Route Candidates

| Method | Endpoint |
|---|---|
| GET | `` |
| GET | `/alerts` |
| POST | `/alerts/generate` |
| PATCH | `/alerts/{alert_id}/resolve` |
| GET | `/` |
| GET | `` |
| GET | `/{profile_name}` |
| GET | `/health` |
| GET | `/health` |

These are static duplicate candidates. Review them manually; router prefixes may affect effective paths.

## Parsing Errors

No Python parsing errors detected.

## Limitations

- This reference scans static HTTP route decorators.
- APIRouter prefixes are not resolved.
- Dynamically registered routes may be absent.
- Authentication and authorization requirements are not inferred.
- Verify endpoint behavior against the running application.
