import csv
import re
import unicodedata
from pathlib import Path


def normalize_text(text):
    if not text:
        return ""

    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # Convert to lowercase
    text = text.casefold()

    # Fold accents on Latin letters only. Combining marks in other scripts
    # can be meaningful (for example, Indic vowel signs and viramas).
    folded = []
    for ch in text:
        if "LATIN" in unicodedata.name(ch, ""):
            decomposed = unicodedata.normalize("NFD", ch)
            folded.extend(
                part for part in decomposed
                if not unicodedata.category(part).startswith("M")
            )
        else:
            folded.append(ch)
    text = "".join(folded)

    # Replace punctuation/symbols with spaces while retaining script marks.
    text = "".join(
        " " if not (re.match(r"\w", ch, flags=re.UNICODE) or ch.isspace()
                    or unicodedata.category(ch).startswith("M")) else ch
        for ch in text
    )

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def compact_text(text):
    return re.sub(r"\s+", "", text)


def process_file(input_file, output_file):

    print(f"\nProcessing: {input_file}")

    with open(
        input_file,
        "r",
        encoding="utf-8",
        newline=""
    ) as infile, open(
        output_file,
        "w",
        encoding="utf-8",
        newline=""
    ) as outfile:

        reader = csv.DictReader(
            infile,
            delimiter="\t"
        )

        original_columns = reader.fieldnames

        new_columns = original_columns + [
            "business_name_norm",
            "business_name_compact",
            "business_address_norm",
            "business_address_compact",
            "country_norm"
        ]

        writer = csv.DictWriter(
            outfile,
            fieldnames=new_columns,
            delimiter="\t"
        )

        writer.writeheader()

        count = 0

        for row in reader:

            name = row.get("business_name", "")
            address = row.get("business_address", "")
            country = row.get("country", "")

            # Normalize fields
            name_norm = normalize_text(name)
            address_norm = normalize_text(address)
            country_norm = normalize_text(country)

            # Add normalized columns
            row["business_name_norm"] = name_norm
            row["business_name_compact"] = compact_text(name_norm)

            row["business_address_norm"] = address_norm
            row["business_address_compact"] = compact_text(address_norm)

            row["country_norm"] = country_norm

            writer.writerow(row)

            count += 1

            if count % 100000 == 0:
                print(f"Processed {count:,} rows")

    print(f"Finished: {count:,} rows")
    print(f"Output: {output_file}")


if __name__ == "__main__":

    DATASET = Path("dataset")
    TRAIN = DATASET / "train"
    OUTPUT = TRAIN / "normalized"

    # Create normalized folder automatically
    OUTPUT.mkdir(exist_ok=True)

    files = [
        "train_source1.tsv",
        "train_source2.tsv",
        "train_source3.tsv"
    ]

    for filename in files:

        input_file = TRAIN / filename
        output_file = OUTPUT / filename

        if not input_file.exists():
            print(f"WARNING: File not found: {input_file}")
            continue

        process_file(
            input_file,
            output_file
        )

    print("\n================================")
    print("NORMALIZATION COMPLETE")
    print("================================")
