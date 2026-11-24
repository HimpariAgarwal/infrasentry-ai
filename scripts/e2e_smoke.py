import os
import sys
from pathlib import Path
from io import BytesIO

import httpx
from dotenv import load_dotenv
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / "backend" / ".env", override=False)

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
USERNAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


def make_test_image():
    image = Image.new("RGB", (512, 512), (85, 85, 85))
    draw = ImageDraw.Draw(image)
    draw.line((256, 0, 256, 512), fill=(220, 220, 220), width=4)
    draw.ellipse((140, 180, 260, 290), fill=(35, 35, 35))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def main():
    if not USERNAME or not PASSWORD:
        raise RuntimeError(
            "ADMIN_USERNAME / ADMIN_PASSWORD backend/.env mein nahi mile."
        )

    with httpx.Client(
        base_url=BASE_URL,
        timeout=180,
        follow_redirects=True
    ) as client:

        print("\n===== HEALTH =====")
        response = client.get("/health")
        check(response.status_code == 200, "Backend health")

        print("\n===== LOGIN =====")
        response = client.post(
            "/api/v1/auth/token",
            data={"username": USERNAME, "password": PASSWORD}
        )
        check(response.status_code == 200, "Admin login")

        token = response.json().get("access_token")
        check(bool(token), "JWT token received")
        headers = {"Authorization": f"Bearer {token}"}

        profile = client.get("/api/v1/auth/me", headers=headers)
        check(profile.status_code == 200, "Authenticated profile")

        print("\n===== READINESS =====")
        readiness = client.get("/api/v1/readiness", headers=headers)
        check(readiness.status_code == 200, "System readiness")

        print("\n===== CREATE REPORT =====")
        payload = {
            "damage_type": "pothole",
            "description": "Day 108 automated smoke test.",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "severity": 3
        }

        created = client.post("/reports", json=payload)
        check(created.status_code in (200, 201), "Create report")

        report_data = created.json().get("report", created.json())
        report_id = report_data.get("id")
        check(bool(report_id), "Report ID received")

        print("\n===== IMAGE UPLOAD =====")
        image_bytes = make_test_image()

        uploaded = client.post(
            f"/images/upload/{report_id}",
            headers=headers,
            files={
                "file": (
                    "day108-test.png",
                    image_bytes,
                    "image/png"
                )
            }
        )
        check(uploaded.status_code == 200, "Image upload")

        upload_data = uploaded.json()
        image_url = upload_data.get("original_image_url")
        check(bool(image_url), "Original image URL returned")

        image_response = client.get(image_url)
        check(image_response.status_code == 200, "Uploaded image accessible")

        print("Image processing:", upload_data.get("processing_status"))

        print("\n===== AI DETECTION =====")
        model_info = client.get("/api/v1/model-info", headers=headers)
        check(model_info.status_code == 200, "AI model info")

        detected = client.post(
            "/api/v1/detect",
            headers=headers,
            params={"confidence": 0.10},
            files={
                "file": (
                    "day108-test.png",
                    image_bytes,
                    "image/png"
                )
            }
        )
        check(detected.status_code == 200, "AI detection")

        result = detected.json()
        check(
            isinstance(result.get("detections"), list),
            "Detection list returned"
        )

        print("Detection count:", result.get("detections_count"))

        print("\n===== DASHBOARD =====")
        analytics = client.get("/analytics/summary")
        check(analytics.status_code == 200, "Dashboard analytics")

        reports = client.get("/reports")
        check(reports.status_code == 200, "Reports list")

        print("\n===== UPDATE REPORT =====")
        updated = client.put(
            f"/reports/{report_id}",
            json={"status": "under_review"}
        )
        check(updated.status_code == 200, "Update report")

        print("\n===== CLEANUP =====")
        deleted = client.delete(f"/reports/{report_id}")
        check(deleted.status_code in (200, 204), "Delete test report")

        print("\nALL DAY 108 CHECKS PASSED.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\n[FAILED] {type(error).__name__}: {error}")
        sys.exit(1)

