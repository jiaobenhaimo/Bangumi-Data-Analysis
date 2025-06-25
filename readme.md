## Appendix C: readme.md
Bangumi-Data-Analysis

This project analyzes how adaptation sources affect anime ratings on Bangumi.tv. It compares mean ratings, within-anime variability, and between-anime consistency across four adaptation categories: original works, manga, game, and light novel adaptations. For detailed methodology and results, see the [Statistical Analysis Report](report.pdf).

### Setup Instructions

#### 1. Clone repo
```
git clone https://github.com/jiaobenhaimo/Bangumi-Data-Analysis.git
cd Bangumi-Data-Analysis
```

#### 2. Create and activate virtual environment
``` 
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

#### 3. Install dependencies
``` 
pip install -r requirements.txt
```

#### 4. Download data
1. Visit [bangumi/Archive](https://github.com/bangumi/Archive)
2. Download the latest data dump
3. Extract and move `subject.jsonlines` to `data/` directory

#### 5. Run analysis
``` 
python main.py
```

### File Structure
```
├── data/                   # Data directory
│   ├── subject.jsonlines   # Raw data from bangumi/Archive
│   ├── data.csv            # Processed dataset
│   ├── sample.csv          # Sampled dataset (n=45 per category)
│   ├── data_stats.csv      # Full dataset statistics
│   └── sample_stats.csv    # Sample dataset statistics
├── venv/                   # Virtual environment
├── main.py                 # Analysis script
├── report.pdf              # Statistical analysis report
├── report.tex              # LaTeX source of the report
├── requirements.txt        # Dependencies
└── README.MD               # This file
```

### Output
The script generates:
1. Processed CSV files in `data/` directory
2. Console output with ANOVA and Levene's test results

This repo is licensed under the BSD 2-Clause License. The data generated from this project follows CC BY-SA license, as required by Bangumi.tv.