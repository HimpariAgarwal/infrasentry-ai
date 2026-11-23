
import csv
import random
import shutil
import xml.etree.ElementTree as ET

from collections import defaultdict, Counter
from pathlib import Path

try:
    from .dataset_config import (
        PROJECT_ROOT,
        DAMAGE_CLASSES,
        MANIFEST_FILE,
        PROCESSED_DIR,
    )
except ImportError:
    from dataset_config import (
        PROJECT_ROOT,
        DAMAGE_CLASSES,
        MANIFEST_FILE,
        PROCESSED_DIR,
    )


SEED = 42
VALIDATION_FRACTION = 0.20

OUTPUT_DIR = PROCESSED_DIR / "rdd2022_yolo"

CLASS_TO_YOLO_ID = {
    code: index
    for index, code in enumerate(DAMAGE_CLASSES)
}


def load_eligible_records():

    records = []

    with MANIFEST_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            baseline = row["baseline_labels"].strip()
            extended = row["extended_labels"].strip()
            unresolved = row["unresolved_labels"].strip()
            unrecognized = row["unrecognized_labels"].strip()
            labels = row["labels"].strip()

            baseline_only = (
                bool(baseline)
                and not extended
                and not unresolved
                and not unrecognized
            )

            genuine_negative = (
                not labels
                and not baseline
                and not extended
                and not unresolved
                and not unrecognized
            )

            if not (baseline_only or genuine_negative):
                continue

            codes = set(baseline.split(";")) if baseline else set()

            if not codes.issubset(CLASS_TO_YOLO_ID):
                raise ValueError(
                    f"Unexpected baseline label: {row['image_path']}"
                )

            records.append({
                "image_path": row["image_path"],
                "annotation_path": row["annotation_path"],
                "labels": codes,
                "negative": genuine_negative,
            })

    return records


def create_split(records):

    rng = random.Random(SEED)

    negatives = [
        record for record in records
        if record["negative"]
    ]

    positives = [
        record for record in records
        if not record["negative"]
    ]

    target_negative_val = round(
        len(negatives) * VALIDATION_FRACTION
    )

    target_positive_val = round(
        len(positives) * VALIDATION_FRACTION
    )

    # Split negative images independently.
    rng.shuffle(negatives)

    negative_validation = negatives[:target_negative_val]

    # Group positive images by exact label combination.
    groups = defaultdict(list)

    for record in positives:
        signature = tuple(sorted(record["labels"]))
        groups[signature].append(record)

    # Shuffle each group reproducibly.
    for group in groups.values():
        rng.shuffle(group)

    # Largest-remainder allocation ensures exact validation size.
    allocations = {}
    remainders = {}

    for signature, group in groups.items():

        exact = len(group) * VALIDATION_FRACTION
        base = int(exact)

        allocations[signature] = base
        remainders[signature] = exact - base

    remaining_slots = (
        target_positive_val - sum(allocations.values())
    )

    signatures = sorted(
        groups.keys(),
        key=lambda signature: (
            -remainders[signature],
            signature
        )
    )

    for signature in signatures[:remaining_slots]:
        allocations[signature] += 1

    positive_validation = []

    for signature, group in groups.items():

        count = allocations[signature]

        positive_validation.extend(
            group[:count]
        )

    validation = negative_validation + positive_validation

    validation_ids = {
        record["image_path"] for record in validation
    }

    training = [
        record for record in records
        if record["image_path"] not in validation_ids
    ]

    rng.shuffle(training)
    rng.shuffle(validation)

    return training, validation


def convert_xml_to_yolo(xml_path):

    root = ET.parse(xml_path).getroot()

    size = root.find("size")

    if size is None:
        raise ValueError(f"Missing image size: {xml_path}")

    width = int(size.findtext("width", "0"))
    height = int(size.findtext("height", "0"))

    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image dimensions: {xml_path}")

    lines = []

    for obj in root.findall("object"):

        code = obj.findtext("name", "").strip()

        if code not in CLASS_TO_YOLO_ID:
            raise ValueError(
                f"Non-baseline label in eligible XML: {code} ({xml_path})"
            )

        box = obj.find("bndbox")

        if box is None:
            raise ValueError(f"Missing bounding box: {xml_path}")

        xmin = float(box.findtext("xmin", "nan"))
        ymin = float(box.findtext("ymin", "nan"))
        xmax = float(box.findtext("xmax", "nan"))
        ymax = float(box.findtext("ymax", "nan"))

        if not (
            0 <= xmin < xmax <= width
            and 0 <= ymin < ymax <= height
        ):
            raise ValueError(
                f"Invalid bounding box in {xml_path}: "
                f"{xmin}, {ymin}, {xmax}, {ymax}"
            )

        x_center = ((xmin + xmax) / 2) / width
        y_center = ((ymin + ymax) / 2) / height
        box_width = (xmax - xmin) / width
        box_height = (ymax - ymin) / height

        class_id = CLASS_TO_YOLO_ID[code]

        lines.append(
            f"{class_id} "
            f"{x_center:.8f} "
            f"{y_center:.8f} "
            f"{box_width:.8f} "
            f"{box_height:.8f}"
        )

    return lines


def print_split_report(training, validation):

    for name, records in (
        ("TRAIN", training),
        ("VALIDATION", validation),
    ):

        class_images = Counter()

        for record in records:
            for code in record["labels"]:
                class_images[code] += 1

        negatives = sum(
            record["negative"] for record in records
        )

        print(f"\n{name}")
        print("-" * 40)
        print("Total images:", len(records))
        print("Negative images:", negatives)

        for code in CLASS_TO_YOLO_ID:
            print(
                f"{code} images: {class_images[code]}"
            )

    print("\nValidation class percentages:")

    train_counts = Counter()
    val_counts = Counter()

    for record in training:
        train_counts.update(record["labels"])

    for record in validation:
        val_counts.update(record["labels"])

    for code in CLASS_TO_YOLO_ID:

        total = train_counts[code] + val_counts[code]

        percentage = (
            val_counts[code] / total * 100
            if total else 0
        )

        print(
            f"{code}: {percentage:.2f}% "
            f"({val_counts[code]}/{total})"
        )


def create_dataset(training, validation):

    if OUTPUT_DIR.exists():
        raise FileExistsError(
            f"Output already exists: {OUTPUT_DIR}\n"
            "Do not overwrite it automatically."
        )

    project_root = PROJECT_ROOT.resolve()

    for split_name, records in (
        ("train", training),
        ("val", validation),
    ):

        image_dir = OUTPUT_DIR / "images" / split_name
        label_dir = OUTPUT_DIR / "labels" / split_name

        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)

        for record in records:

            source_image = (
                project_root / record["image_path"]
            ).resolve()

            source_xml = (
                project_root / record["annotation_path"]
            ).resolve()

            if not source_image.is_file():
                raise FileNotFoundError(source_image)

            if not source_xml.is_file():
                raise FileNotFoundError(source_xml)

            destination_image = image_dir / source_image.name
            destination_label = (
                label_dir / f"{source_image.stem}.txt"
            )

            if destination_image.exists():
                raise FileExistsError(destination_image)

            yolo_lines = convert_xml_to_yolo(source_xml)

            shutil.copy2(source_image, destination_image)

            destination_label.write_text(
                "\n".join(yolo_lines),
                encoding="utf-8"
            )

    yaml_lines = [
        "path: .",
        "train: images/train",
        "val: images/val",
        "",
        "names:",
    ]

    for code, class_id in CLASS_TO_YOLO_ID.items():
        yaml_lines.append(
            f"  {class_id}: '{DAMAGE_CLASSES[code]}'"
        )

    (OUTPUT_DIR / "data.yaml").write_text(
        "\n".join(yaml_lines) + "\n",
        encoding="utf-8"
    )

    print("\nYOLO dataset created:", OUTPUT_DIR)


def main():

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--execute",
        action="store_true"
    )

    args = parser.parse_args()

    print("Loading eligible dataset records...")

    records = load_eligible_records()

    print("Eligible images:", len(records))

    if len(records) != 6650:
        raise ValueError(
            f"Expected 6650 images, found {len(records)}"
        )

    training, validation = create_split(records)

    if len(training) != 5320 or len(validation) != 1330:
        raise ValueError("Unexpected split sizes.")

    print_split_report(training, validation)

    print("\nRandom seed:", SEED)

    if not args.execute:
        print("\nDRY RUN COMPLETE.")
        print("No files were copied.")
        print("Review the distribution before execution.")
        return

    create_dataset(training, validation)


if __name__ == "__main__":
    main()
