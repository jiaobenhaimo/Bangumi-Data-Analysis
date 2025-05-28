import csv
import json
from collections import defaultdict

def count_tags(jsonl_path: str) -> dict:
    tag_counter = defaultdict(int)
    
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                subject = json.loads(line.strip())
                if subject.get("type") != 2:
                    continue
                
                all_tags = []
                for tag in subject.get("tags", []):
                    if "name" in tag:
                        all_tags.append(tag["name"])
                all_tags.extend(subject.get("meta_tags", []))
                
                for tag in all_tags:
                    if "改" in tag or "原创" in tag:
                        tag_counter[tag] += 1
                        
            except json.JSONDecodeError:
                continue
    
    return tag_counter

def export_to_csv(tag_counts: dict, csv_path: str) -> None:

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Tag", "Time"])
        sorted_tags = sorted(tag_counts.items(), key=lambda x: -x[1])
        for tag, count in sorted_tags:
            writer.writerow([tag, count])

if __name__ == "__main__":
    input_path = "data/subject.jsonlines"
    output_path = "data/tag_counts.csv"
    
    counts = count_tags(input_path)
    export_to_csv(counts, output_path)