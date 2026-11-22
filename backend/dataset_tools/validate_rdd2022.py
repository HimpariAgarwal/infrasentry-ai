
import csv
import json
import xml.etree.ElementTree as ET

from collections import Counter, defaultdict
from pathlib import Path

try:
    from .dataset_config import (
        PROJECT_ROOT,
        DATASET_ROOT,
        PROCESSED_DIR,
        IMAGE_EXTENSIONS,
        DAMAGE_CLASSES,
        EXTENDED_DAMAGE_CLASSES,
        KNOWN_DAMAGE_CLASSES,
        EXCLUDED_FROM_BASELINE_CLASSES,
        UNRESOLVED_LABELS,
        CLASS_TO_ID,
        COUNTRIES,
        MANIFEST_FILE,
        REPORT_FILE,
    )
except ImportError:
    from dataset_config import (
        PROJECT_ROOT,
        DATASET_ROOT,
        PROCESSED_DIR,
        IMAGE_EXTENSIONS,
        DAMAGE_CLASSES,
        EXTENDED_DAMAGE_CLASSES,
        KNOWN_DAMAGE_CLASSES,
        EXCLUDED_FROM_BASELINE_CLASSES,
        UNRESOLVED_LABELS,
        CLASS_TO_ID,
        COUNTRIES,
        MANIFEST_FILE,
        REPORT_FILE,
    )


def find_country(path):
    for part in path.parts:
        for country in COUNTRIES:
            if part.lower() == country.lower():
                return country

    return "Unknown"


def find_split(path):
    for part in path.parts:
        if part.lower() in {"train", "test"}:
            return part.lower()

    return "Unknown"


def build_image_indexes(image_files):
    stem_index = defaultdict(list)
    filename_index = defaultdict(list)

    for image_path in image_files:
        stem_index[image_path.stem.lower()].append(image_path)
        filename_index[image_path.name.lower()].append(image_path)

    return stem_index, filename_index


def find_matching_image(
    xml_path,
    xml_root,
    stem_index,
    filename_index
):
    # 1. Match XML and image in the same folder.
    same_folder = [
        image
        for image in stem_index.get(xml_path.stem.lower(), [])
        if image.parent == xml_path.parent
    ]

    if len(same_folder) == 1:
        return same_folder[0]

    # 2. Match using the filename inside XML.
    filename = xml_root.findtext("filename")

    if filename:
        candidate_name = Path(
            filename.strip().replace("\\", "/")
        ).name

        candidate = xml_path.parent / candidate_name

        if candidate.is_file():
            return candidate

        matches = filename_index.get(
            candidate_name.lower(), []
        )

        if len(matches) == 1:
            return matches[0]

    # 3. Match using a unique filename stem.
    matches = stem_index.get(xml_path.stem.lower(), [])

    if len(matches) == 1:
        return matches[0]

    return None


def read_annotation(xml_root):
    width = xml_root.findtext("size/width")
    height = xml_root.findtext("size/height")

    if width is None or height is None:
        raise ValueError("Missing image dimensions in XML.")

    width = int(width)
    height = int(height)

    if width <= 0 or height <= 0:
        raise ValueError("Invalid image dimensions.")

    labels = []
    invalid_boxes = 0

    for obj in xml_root.findall("object"):
        label = obj.findtext("name")

        if not label:
            raise ValueError("Object has no class label.")

        label = label.strip()
        labels.append(label)

        box = obj.find("bndbox")

        if box is None:
            invalid_boxes += 1
            continue

        try:
            xmin = float(box.findtext("xmin"))
            ymin = float(box.findtext("ymin"))
            xmax = float(box.findtext("xmax"))
            ymax = float(box.findtext("ymax"))

            if not (
                0 <= xmin < xmax <= width
                and 0 <= ymin < ymax <= height
            ):
                invalid_boxes += 1

        except (TypeError, ValueError):
            invalid_boxes += 1

    return width, height, labels, invalid_boxes


def classify_labels(labels):
    baseline = [
        label for label in labels
        if label in DAMAGE_CLASSES
    ]

    extended = [
        label for label in labels
        if label in EXCLUDED_FROM_BASELINE_CLASSES
    ]

    unresolved = [
        label for label in labels
        if label in UNRESOLVED_LABELS
    ]

    unrecognized = [
        label for label in labels
        if label not in KNOWN_DAMAGE_CLASSES
        and label not in UNRESOLVED_LABELS
    ]

    return baseline, extended, unresolved, unrecognized


def main():
    print("\nINFRA SENTRY AI")
    print("RDD2022 DATASET VALIDATION")
    print("-" * 50)

    if not DATASET_ROOT.exists():
        print("Dataset folder not found!")
        print("Expected location:", DATASET_ROOT)
        return

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Scanning dataset files...")

    image_files = [
        path
        for path in DATASET_ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    ]

    xml_files = [
        path
        for path in DATASET_ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() == ".xml"
    ]

    print("Images found:", len(image_files))
    print("XML annotations found:", len(xml_files))

    if not image_files:
        print("No images found. Check extracted dataset folders.")
        return

    print("\nBuilding image indexes...")

    stem_index, filename_index = build_image_indexes(image_files)

    print("Image indexes ready.")
    print("\nMatching annotations...")

    class_counts = Counter()

    unmatched_annotations = []
    invalid_annotations = []
    manifest_rows = []

    matched_count = 0
    total_objects = 0
    invalid_boxes_count = 0

    baseline_object_count = 0
    extended_object_count = 0
    unresolved_object_count = 0
    unrecognized_object_count = 0

    for number, xml_path in enumerate(xml_files, start=1):
        try:
            # Parse every XML only once.
            xml_root = ET.parse(xml_path).getroot()

            image_path = find_matching_image(
                xml_path,
                xml_root,
                stem_index,
                filename_index
            )

            if image_path is None:
                unmatched_annotations.append(str(xml_path))
                continue

            width, height, labels, invalid_boxes = read_annotation(
                xml_root
            )

            baseline, extended, unresolved, unrecognized = (
                classify_labels(labels)
            )

            matched_count += 1
            total_objects += len(labels)
            invalid_boxes_count += invalid_boxes

            class_counts.update(labels)

            baseline_object_count += len(baseline)
            extended_object_count += len(extended)
            unresolved_object_count += len(unresolved)
            unrecognized_object_count += len(unrecognized)

            manifest_rows.append({
                "image_path": str(
                    image_path.relative_to(PROJECT_ROOT)
                ),
                "annotation_path": str(
                    xml_path.relative_to(PROJECT_ROOT)
                ),
                "country": find_country(image_path),
                "split": find_split(image_path),
                "width": width,
                "height": height,
                "object_count": len(labels),
                "labels": ";".join(labels),
                "baseline_labels": ";".join(baseline),
                "extended_labels": ";".join(extended),
                "unresolved_labels": ";".join(unresolved),
                "unrecognized_labels": ";".join(unrecognized),
                "invalid_boxes": invalid_boxes,
            })

        except (ET.ParseError, ValueError, OSError) as error:
            invalid_annotations.append({
                "file": str(xml_path),
                "error": str(error),
            })

        if number % 500 == 0:
            print(
                f"Processed {number}/{len(xml_files)} "
                "annotations..."
            )

    # Generate manifest.
    fieldnames = [
        "image_path",
        "annotation_path",
        "country",
        "split",
        "width",
        "height",
        "object_count",
        "labels",
        "baseline_labels",
        "extended_labels",
        "unresolved_labels",
        "unrecognized_labels",
        "invalid_boxes",
    ]

    with open(
        MANIFEST_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(manifest_rows)

    # Separate class counts.
    baseline_counts = {
        code: class_counts.get(code, 0)
        for code in DAMAGE_CLASSES
    }

    extended_counts = {
        code: class_counts.get(code, 0)
        for code in EXTENDED_DAMAGE_CLASSES
    }

    unresolved_counts = {
        code: class_counts.get(code, 0)
        for code in UNRESOLVED_LABELS
    }

    unrecognized_counts = {
        label: count
        for label, count in class_counts.items()
        if label not in KNOWN_DAMAGE_CLASSES
        and label not in UNRESOLVED_LABELS
    }

    # Detailed validation report.
    report = {
        "dataset": "RDD2022",
        "dataset_root": str(DATASET_ROOT),

        "total_images": len(image_files),
        "total_xml_annotations": len(xml_files),
        "matched_annotations": matched_count,
        "unmatched_annotations": len(unmatched_annotations),
        "invalid_annotations": len(invalid_annotations),

        "total_damage_objects": total_objects,
        "invalid_bounding_boxes": invalid_boxes_count,

        "baseline_training_classes": {
            "class_ids": CLASS_TO_ID,
            "class_counts": baseline_counts,
            "total_objects": baseline_object_count,
        },

        "extended_known_classes": {
            "class_counts": extended_counts,
            "total_objects": extended_object_count,
        },

        "unresolved_labels": {
            "class_counts": unresolved_counts,
            "total_objects": unresolved_object_count,
        },

        "unrecognized_labels": {
            "class_counts": unrecognized_counts,
            "total_objects": unrecognized_object_count,
        },

        "all_class_counts": dict(class_counts),

        "unmatched_annotation_files": unmatched_annotations,

        "invalid_annotation_details": invalid_annotations,

        "manifest_file": str(MANIFEST_FILE),
        "report_file": str(REPORT_FILE),

        "validation_status": (
            "completed"
            if matched_count > 0
            else "no_valid_annotations"
        ),
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as json_file:

        json.dump(report, json_file, indent=4)

    # Console results.
    print("\nVALIDATION RESULTS")
    print("-" * 50)

    print("Total images:", len(image_files))
    print("Total annotations:", len(xml_files))
    print("Matched annotations:", matched_count)
    print("Unmatched annotations:", len(unmatched_annotations))
    print("Invalid annotations:", len(invalid_annotations))
    print("Total damage objects:", total_objects)
    print("Invalid bounding boxes:", invalid_boxes_count)

    print("\nFOUR-CLASS BASELINE")

    for code, name in DAMAGE_CLASSES.items():
        print(
            f"{code} - {name}: "
            f"{baseline_counts[code]}"
        )

    print("\nADDITIONAL KNOWN CLASSES")

    for code, name in EXTENDED_DAMAGE_CLASSES.items():
        print(
            f"{code} - {name}: "
            f"{extended_counts[code]}"
        )

    print("\nUNRESOLVED LABELS:", unresolved_counts)

    print("\nUNRECOGNIZED LABELS:", unrecognized_counts)

    print("\nOBJECT CATEGORY TOTALS")
    print("Baseline objects:", baseline_object_count)
    print("Extended objects:", extended_object_count)
    print("Unresolved objects:", unresolved_object_count)
    print("Unrecognized objects:", unrecognized_object_count)

    print("\nManifest saved:", MANIFEST_FILE)
    print("Report saved:", REPORT_FILE)

    print("\nDATASET VALIDATION FINISHED")


if __name__ == "__main__":
    main()
