import csv
import json
import pandas as pd
import math
import scipy.stats as stats
import random
import os
from typing import Dict, List

CATEGORY_MAP = [
    (4, ["轻小说改", "小说改", "LN改", "轻改", "小说改编", "轻小说改编"]),
    (3, ["游戏改", "GAL改", "视觉小说改", "游戏改编", "游改", "galgame改", "遊戲改", "GAL改编"]),
    (2, ["漫画改", "漫改", "漫画改编"]),
    (1, ["原创", "原创动画"])
]

def has_japan_tag(subject: Dict) -> bool:
    japan_tag = False
    tv_tag = False
    
    for tag in subject.get("tags", []):
        if tag.get("name") == "日本":
            japan_tag = True
        if tag.get("name") == "TV":
            tv_tag = True
    
    for mtag in subject.get("meta_tags", []):
        if mtag == "日本":
            japan_tag = True
        if mtag == "TV":
            tv_tag = True
        
    return japan_tag and tv_tag

def classify_subject(subject: Dict) -> int:
    all_tags = []
    for tag in subject.get("tags", []):
        if "name" in tag:
            all_tags.append(tag["name"])
    all_tags.extend(subject.get("meta_tags", []))
    
    for cat_id, keywords in CATEGORY_MAP:
        for kw in keywords:
            if any(kw in tag for tag in all_tags):
                return cat_id
    
    return 0

def sort_subject(output_path: str) -> None:
    df = pd.read_csv(output_path)
    sorted_df = df.sort_values(by=["Adapted From", "Date", "ID"], ascending=True)
    sorted_df.to_csv(output_path, index=False)

def process_subject(subject: Dict) -> Dict:
    score_details = subject.get("score_details", {})
    scores = [score_details.get(str(i), 0) for i in range(1, 11)]
    total = sum(scores)
    
    if total < 30:
        return None

    weighted_sum = sum(i * score for i, score in enumerate(scores, start=1))
    mean = weighted_sum / total
    variance = sum(score * (i - mean)**2 for i, score in enumerate(scores, start=1)) / total
    sd = math.sqrt(variance)

    return {
        "ID": subject["id"],
        "Date": subject.get("date", "")[:4],
        "Adapted From": classify_subject(subject),
        **{str(i): scores[i-1] for i in range(1, 11)},
        "Sum": total,
        "Mean": mean,
        "Standard Deviation": sd
    }

def process_jsonl(input_path: str, output_path: str) -> None:
    data = []
    
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                subject = json.loads(line.strip())
                if (subject.get("type") != 2 or 
                    not has_japan_tag(subject) or 
                    not subject.get("date")):
                    continue
                
                if row := process_subject(subject):
                    data.append(row)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing line: {str(e)}")
    
    # Create and save DataFrame
    df = pd.DataFrame(data)
    if not df.empty:
        df.sort_values(by=["Adapted From", "Date", "ID"], inplace=True)
        df.to_csv(output_path, index=False)

def generate_stats(data_path: str, stats_path: str) -> None:
    """Generate statistics from a CSV file and save to another CSV"""
    df = pd.read_csv(data_path)
    stats = []
    categories = [0] + [cat_id for cat_id, _ in CATEGORY_MAP]
    
    # Overall statistics (category 0)
    overall_stats = calculate_category_stats(df, 0)
    stats.append([0] + overall_stats)
    
    # Category-specific statistics
    for cat_id, _ in CATEGORY_MAP:
        cat_df = df[df["Adapted From"] == cat_id]
        cat_stats = calculate_category_stats(cat_df, cat_id)
        stats.append([cat_id] + cat_stats)
    
    # Save statistics
    stats_df = pd.DataFrame(stats, columns=[
        "Adapted From", "Entries", "Mean", "Entry Spread", "Rating Spread"
    ])
    stats_df.to_csv(stats_path, index=False)

def calculate_category_stats(df: pd.DataFrame, category: int) -> List[float]:
    """Calculate statistics for a specific category"""
    if df.empty:
        return [0, 0.0, 0.0, 0.0]
    
    entries = len(df)
    mean = df["Mean"].mean()
    entry_spread = df["Standard Deviation"].mean()
    rating_spread = df["Mean"].std(ddof=0)  # Population standard deviation
    
    return [entries, mean, entry_spread, rating_spread]

def random_sample(input_path: str, output_path: str, n: int = 40) -> None:
    """Create random sample with n entries per category"""
    df = pd.read_csv(input_path)
    samples = []
    
    for cat_id, _ in CATEGORY_MAP:
        cat_df = df[df["Adapted From"] == cat_id]
        if len(cat_df) > 0:
            samples.append(cat_df.sample(min(n, len(cat_df)), replace=False))
    
    if samples:
        pd.concat(samples).to_csv(output_path, index=False)

def chi_gof(data_path: str) -> None:
    # numEntries=[0,0,0,0,0]
    sumMean=[0,0,0,0,0]
    sumSD=[0,0,0,0,0]
    ratingsd=[0,0,0,0,0]
    with open(data_path, "r", newline="", encoding="utf-8-sig") as statsfile:
        line=list(statsfile)[1:]
        for i in range(5):
            row=line[i].split(',')
            # numEntries[i]=int(row[1])/4
            sumMean[i]=float(row[2])
            sumSD[i]=float(row[3])
            ratingsd[i]=float(row[4])

def anova_test(data_path: str) -> None:
    df = pd.read_csv(data_path)
    categories = [1, 2, 3, 4]  # Only specific adaptation categories
    
    print("One-way ANOVA results:")
    
    # 1. ANOVA for Mean Ratings (Between-Work Differences)
    groups_mean = [df[df['Adapted From'] == cat]['Mean'] for cat in categories]
    f_stat_mean, p_value_mean = stats.f_oneway(*groups_mean)
    print(f"Mean ratings: F-statistic = {f_stat_mean:.4f}, p-value = {p_value_mean:.4f}")
    
    # 2. ANOVA for Entry Spread (Within-Work Variability)
    groups_sd = [df[df['Adapted From'] == cat]['Standard Deviation'] for cat in categories]
    f_stat_sd, p_value_sd = stats.f_oneway(*groups_sd)
    print(f"Entry spread: F-statistic = {f_stat_sd:.4f}, p-value = {p_value_sd:.4f}")
    
    # 3. ANOVA for Rating Spread (Category-Level Consistency)
    # Prepare data: For each category, calculate the SD of the means
    category_stats = []
    for cat in categories:
        cat_means = df[df['Adapted From'] == cat]['Mean']
        # Create multiple observations: SD value repeated for each anime in category
        sd_value = cat_means.std(ddof=0)
        category_stats.extend([(cat, sd_value)] * len(cat_means))
    
    rating_spread_df = pd.DataFrame(category_stats, columns=['Adapted From', 'Rating_Spread'])
    groups_rating_spread = [
        rating_spread_df[rating_spread_df['Adapted From'] == cat]['Rating_Spread'] 
        for cat in categories
    ]
    f_stat_rs, p_value_rs = stats.f_oneway(*groups_rating_spread)
    print(f"Rating spread: F-statistic = {f_stat_rs:.4f}, p-value = {p_value_rs:.4f}")
    
    # Report category-level rating spread values
    rating_spread_values = [group.iloc[0] for group in groups_rating_spread]
    print(f"Rating spread values: {rating_spread_values}")

if __name__ == "__main__":
    os.system("rm -rf data/*.csv")
    process_jsonl("data/subject.jsonlines", "data/data.csv")
    generate_stats("data/data.csv", "data/data_stats.csv")
    random_sample("data/data.csv", "data/sample.csv")
    generate_stats("data/sample.csv", "data/sample_stats.csv")
    anova_test("data/sample.csv")


if __name__ == "__main__":
    os.system("rm -rf data/*.csv")
    process_jsonl("data/subject.jsonlines", "data/data.csv")
    generate_stats("data/data.csv", "data/data_stats.csv")
    random_sample("data/data.csv", "data/sample.csv")
    generate_stats("data/sample.csv", "data/sample_stats.csv")
    chi_gof("data/sample_stats.csv")