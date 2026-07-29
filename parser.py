import json
import re
from pathlib import Path


# -----------------------------
# Load Config
# -----------------------------

with open(Path("config.json"), "r", encoding="utf-8") as f:
    CONFIG = json.load(f)


MERCHANTS = CONFIG["merchants"]
CATEGORY_KEYWORDS = CONFIG["categoryKeywords"]
INCOME_KEYWORDS = [k.lower() for k in CONFIG["incomeKeywords"]]


# -----------------------------
# Amount Extraction
# -----------------------------

def extract_amount(text: str) -> float:
    """
    Supports:
        500
        1,250
        ₹500
        rs500
        1.5k
        2k
        2l
        2L
    """

    text = text.lower().replace(",", "")

    match = re.search(
        r'(?:₹|rs\.?\s*)?(\d+(?:\.\d+)?)([kl]?)',
        text
    )

    if not match:
        raise ValueError("Amount not found")

    value = float(match.group(1))
    suffix = match.group(2)

    if suffix == "k":
        value *= 1000

    elif suffix == "l":
        value *= 100000

    return round(value, 2)


# -----------------------------
# Merchant Detection
# -----------------------------

def detect_merchant(text: str) -> str:

    lower = text.lower()

    for merchant, keywords in MERCHANTS.items():

        for keyword in keywords:

            if keyword.lower() in lower:
                return merchant

    return "Unknown"


# -----------------------------
# Income Detection
# -----------------------------

def detect_type(text: str) -> str:

    lower = text.lower()

    for keyword in INCOME_KEYWORDS:

        if keyword in lower:
            return "income"

    return "expense"


# -----------------------------
# Category Detection
# -----------------------------

def detect_category(text: str, txn_type: str) -> str:

    if txn_type == "income":
        return "income"

    lower = text.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():

        for keyword in keywords:

            if keyword.lower() in lower:
                return category

    return "other"


# -----------------------------
# Clean Note
# -----------------------------

def clean_note(text: str) -> str:

    note = text

    note = re.sub(r'₹', '', note, flags=re.IGNORECASE)
    note = re.sub(r'rs\.?', '', note, flags=re.IGNORECASE)
    note = re.sub(r'\d+(?:\.\d+)?[kl]?', '', note)

    note = re.sub(r'\s+', ' ', note).strip()

    if note == "":
        return "No description"

    return note.title()


# -----------------------------
# Parse Message
# -----------------------------

def parse_message(text: str):

    amount = extract_amount(text)

    txn_type = detect_type(text)

    merchant = detect_merchant(text)

    category = detect_category(text, txn_type)

    note = clean_note(text)

    if txn_type == "income" and merchant == "Unknown":
        merchant = "Income"

    return {

        "amount": amount,

        "merchant": merchant,

        "category": category,

        "note": note,

        "type": txn_type

    }


# -----------------------------
# Testing
# -----------------------------

if __name__ == "__main__":

    tests = [

        "Swiggy dinner 420",

        "Uber airport 650",

        "Salary 75000",

        "Refund Amazon 350",

        "Blinkit groceries 1800",

        "Electricity bill 2500",

        "Invested 15k in SIP",

        "Coffee 150",

        "Netflix 649",

        "Cigarette 130"

    ]

    for test in tests:

        print("-" * 60)

        print(test)

        print(parse_message(test))