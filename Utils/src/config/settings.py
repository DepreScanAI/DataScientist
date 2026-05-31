# Nilai sentinel NHANES untuk angka 0 dalam format XPT (floating-point encoding dari integer 0 dalam format XDR IEEE-754 extended dengan exponent bias SAS).
# Dalam pandas read_sas, angka 0 di-encode sebagai 5.397605e-79.
SENTINEL_ZERO = 5.397605346934028e-79
SENTINEL_ZERO_TOL = 1e-70   # toleransi perbandingan floating-point

# Kode NHANES untuk "Refused" dan "Don't Know"
NHANES_REFUSED   = [7, 77, 777]
NHANES_DONTKNOW  = [9, 99, 999]
NHANES_MISSING_CODES = NHANES_REFUSED + NHANES_DONTKNOW

# Path default - ubah sesuai lokasi file
RAW_DATA_DIR = "data/raw/"

RAW_PATHS = {
    "DEMO_J": f"{RAW_DATA_DIR}DEMO_J.xpt",
    "ALQ_J":  f"{RAW_DATA_DIR}ALQ_J.xpt",
    "DPQ_J":  f"{RAW_DATA_DIR}DPQ_J.xpt",
    "PAQ_J":  f"{RAW_DATA_DIR}PAQ_J.xpt",
    "SLQ_J":  f"{RAW_DATA_DIR}SLQ_J.xpt",
}

OUTPUT_DIR = "outputs"
O_DATASET = ["data/interim", "data/processed"]
O_PLOT = f"{OUTPUT_DIR}/plot"
O_JSON = f"{OUTPUT_DIR}/json"
O_ABTEST = f"{OUTPUT_DIR}/abtest"

# Mapping kode NHANES ke label human-readable atau yang mudah dipahami manusia

# RIAGENDR: 1=Male, 2=Female
GENDER_MAP = {1: "Male", 2: "Female"}

# RIDRETH3: Race/Hispanic origin (6-level)
RACE_MAP = {
    1: "Mexican American",
    2: "Other Hispanic",
    3: "Non-Hispanic White",
    4: "Non-Hispanic Black",
    6: "Non-Hispanic Asian",
    7: "Other/Multi-Racial",
}

# DMDEDUC2: Education level (adults 20+)
# 1=Less than 9th grade, 2=9-11th grade, 3=HS graduate/GED, 4=Some college/AA, 5=College graduate+, 7=Refused, 9=Don't know
EDUC_MAP = {
    1: "< 9th grade",
    2: "9-11th grade",
    3: "HS/GED",
    4: "Some college/AA",
    5: "College graduate+",
}

# DMDMARTL: Marital status
# 1=Married, 2=Widowed, 3=Divorced, 4=Separated, 5=Never married, 6=Living with partner, 77=Refused
MARITAL_MAP = {
    1: "Married",
    2: "Widowed",
    3: "Divorced",
    4: "Separated",
    5: "Never married",
    6: "Living with partner",
}

# INDHHIN2: Annual household income
# 1=<$5k, 2=$5-10k, 3=$10-15k, 4=$15-20k, 5=$20-25k, 6=$25-35k, 7=$35-45k, 8=$45-55k, 9=$55-65k, 10=$65-75k,
# 12=$20k+, 13=$75k+, 14=$75-100k, 15=≥$100k, 77=Refused, 99=Don't know
INCOME_MAP = {
    1: "<$5k", 2: "$5-10k", 3: "$10-15k", 4: "$15-20k", 5: "$20-25k",
    6: "$25-35k", 7: "$35-45k", 8: "$45-55k", 9: "$55-65k", 10: "$65-75k",
    12: "$20k+", 13: "$75k+", 14: "$75-100k", 15: "≥$100k",
}

# ALQ111: Drank at least 12 drinks in lifetime? 1=Yes, 2=No
# ALQ121: Past 12 months, how often? 0=Never, 1=Every day, 2=5-6/wk,
# 3=3-4/wk, 4=2/wk, 5=1/wk, 6=2-3/month, 7=1/month, 8=7-11/yr, 9=3-6/yr, 10=1-2/yr
ALQ121_LABEL = {
    0: "Never past 12 months",
    1: "Every day",
    2: "5-6 days/week",
    3: "3-4 days/week",
    4: "2 days/week",
    5: "1 day/week",
    6: "2-3 days/month",
    7: "About 1 day/month",
    8: "7-11 days in past year",
    9: "3-6 days in past year",
    10: "1-2 days in past year",
}

# ALQ130: Avg drinks per day on drinking days (actual count, 1-15+)
# ALQ151: Binge drinking past year? 1=Yes, 2=No

# DPQ010–DPQ090: PHQ-9 items (Patient Health Questionnaire)
# Nilai: 0=Not at all, 1=Several days, 2=More than half the days, 3=Nearly every day
# 7=Refused, 9=Don't know
# DPQ100: Difficulty level 0=Not difficult, 1=Somewhat, 2=Very, 3=Extremely
PHQ9_ITEMS = ["DPQ010","DPQ020","DPQ030","DPQ040","DPQ050",
               "DPQ060","DPQ070","DPQ080","DPQ090"]
PHQ9_ITEM_LABELS = {
    "DPQ010": "Little interest/pleasure in doing things",
    "DPQ020": "Feeling down, depressed, or hopeless",
    "DPQ030": "Trouble falling/staying asleep, or sleeping too much",
    "DPQ040": "Feeling tired or having little energy",
    "DPQ050": "Poor appetite or overeating",
    "DPQ060": "Feeling bad about yourself",
    "DPQ070": "Trouble concentrating",
    "DPQ080": "Moving/speaking slowly OR being fidgety/restless",
    "DPQ090": "Thoughts of self-harm or being better off dead",
}

# PHQ-9 Depression severity thresholds (Kroenke et al., 2001)
PHQ9_THRESHOLDS = {
    "Minimal":   (0,  4),
    "Mild":      (5,  9),
    "Moderate":  (10, 14),
    "Moderately Severe": (15, 19),
    "Severe":    (20, 27),
}

# PAQ605: Vigorous work activity? 1=Yes, 2=No
# PAQ620: Moderate work activity? 1=Yes, 2=No
# PAQ635: Walk/bicycle transport? 1=Yes, 2=No
# PAQ650: Vigorous recreational? 1=Yes, 2=No
# PAQ665: Moderate recreational? 1=Yes, 2=No
# PAD615: Vigorous work mins/day
# PAD630: Moderate work mins/day
# PAD645: Walk transport mins/day
# PAD660: Vigorous rec mins/day
# PAD675: Moderate rec mins/day
# PAD680: Sedentary minutes per day (9999=Don't know)

# SLD012: Weekday sleep hours (reported, continuous)
# SLD013: Weekend sleep hours (reported, continuous)
# SLQ030: Snoring frequency 0=Never/rare, 1=1-2nights/wk, 2=3-4nights/wk, 3=5+nights/wk, 7=Refused, 9=Don't know
# SLQ040: Snorting/stop breathing freq (same codes)
# SLQ050: Ever told doctor had sleep trouble? 1=Yes, 2=No
# SLQ120: Feel unrested during day? 0=Never, 1=Once, 2=2-4×, 3=5-14×, 4=15-21×, 5=Daily, 9=DK

# PHQ-9 label yang akan dijadikan target
# Paper acuan: https://therapistsupport.rula.com/hc/en-us/articles/23773157055259-Interpreting-PHQ-9-Scores
DEPRESSION_LABEL_MAP = {
    "Minimal":            0,
    "Mild":               1,
    "Moderate":           2,
    "Moderately Severe":  3,
    "Severe":             4,
}