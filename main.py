import csv
import json
import pandas as pd
from typing import Dict
import math


CATEGORY_MAP = [
    (4, ["轻小说改", "小说改", "LN改","轻改","小说改编","轻小说改编"]),
    (3, ["游戏改", "GAL改", "视觉小说改","游戏改编","游改","galgame改","遊戲改","GAL改编"]),
    (2, ["漫画改","漫改", "漫画改编"]),
    (1, ["原创","原创动画"])
]

numEntries=[0,0,0,0,0]
sumMean=[0,0,0,0,0]
sumSD=[0,0,0,0,0]

def has_japan_tag(subject: Dict) -> bool:
    
    r=0
    s=0
    for tag in subject.get("tags", []):
        if tag.get("name")=="日本":
            r=1
        if tag.get("name")=="TV":
            s=1
    
    for mtag in subject.get("meta_tags", []):
        if mtag=="日本":
            r=1
        if mtag=="TV":
            s=1
        
    return r and s

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
    sorted_df = df.sort_values(by=["Adapted From","Date","ID"], ascending=True)
    sorted_df.to_csv(output_path, index=False)

def rating_sd(input_path: str) -> list:
    sd=[0,0,0,0,0]
    with open(input_path, "r", newline="", encoding="utf-8-sig") as statsfile:
        for line in list(statsfile)[1:]:
            row=line.split(',')
            type=int(row[2])
            val=float(row[14])
            sd[type]=sd[type]+(val-sumMean[type])*(val-sumMean[type])
            sd[0]=sd[0]+(val-sumMean[0])*(val-sumMean[0])
    for i in range(5):
        sd[i]=math.sqrt(sd[i]/numEntries[i])
    return sd

def process_jsonl(input_path: str, output_path: str, stats_path: str) -> None:

    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "ID", "Date", "Adapted From",
            "1", "2", "3", "4", "5",
            "6", "7", "8", "9", "10",
            "Sum","Mean","Standard Deviation"
        ])
        
        with open(input_path, "r", encoding="utf-8") as jsonlfile:
            for line in jsonlfile:
                try:
                    subject = json.loads(line.strip())
                    if subject.get("type") != 2:
                        continue
                    if not has_japan_tag(subject):
                        continue
                    if classify_subject(subject)==0:
                        continue
                    if subject.get("date")=="":
                        continue
                    
                    category = classify_subject(subject)
                    
                    score_details = subject.get("score_details", {})
                    score_row = [score_details.get(str(i), 0) for i in range(1, 11)]
                    s=sum(score_row)

                    if s<30:
                        continue

                    id=category
                    mean=sum([score_details.get(str(i), 0)*i for i in range(1, 11)])/s
                    sd=math.sqrt(sum([score_details.get(str(i), 0)*(i-mean)*(i-mean) for i in range(1, 11)])/s)

                    numEntries[id]=numEntries[id]+1
                    sumMean[id]=sumMean[id]+mean
                    sumSD[id]=sumSD[id]+sd

                    numEntries[0]=numEntries[0]+1
                    sumMean[0]=sumMean[0]+mean
                    sumSD[0]=sumSD[0]+sd
                
                    writer.writerow([
                        subject["id"],
                        subject.get("date")[:4],
                        category,
                        *score_row,
                        s,
                        mean,
                        sd
                    ])
                
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error{line[:50]}--{str(e)}")
    for i in range(5):
        num=numEntries[i]
        sumMean[i]=sumMean[i]/num
        sumSD[i]=sumSD[i]/num

    sort_subject(output_path)

    with open(stats_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Adapted From","Entries","Mean","Entry Spread","Rating Spread"
        ])
        ratingsd=rating_sd(output_path)

        for i in range (5):
            writer.writerow([i,numEntries[i],sumMean[i],sumSD[i],ratingsd[i]])

if __name__ == "__main__":
    process_jsonl("data/subject.jsonlines", "data/data.csv", "data/stats.csv")