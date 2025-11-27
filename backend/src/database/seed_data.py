import sqlite3
from datetime import datetime
from .fraud_db import init_database, DB_PATH, get_all_cases

FRAUD_CASES = [
    {
        "userName": "John",
        "securityQuestion": "What is your mother's maiden name?",
        "securityAnswer": "perry",
        "cardEnding": "4242",
        "transactionAmount": "$1,299.99",
        "transactionName": "TechZone Electronics",
        "transactionTime": "November 25, 2025 at 3:42 PM",
        "transactionCategory": "Electronics",
        "transactionSource": "techzone.com",
        "transactionLocation": "Newark, New Jersey",
    },
    {
        "userName": "Sarah",
        "securityQuestion": "What was the name of your first pet?",
        "securityAnswer": "Buddy",
        "cardEnding": "8891",
        "transactionAmount": "$499.00",
        "transactionName": "LuxuryWatch Co",
        "transactionTime": "November 25, 2025 at 11:23 AM",
        "transactionCategory": "Jewelry",
        "transactionSource": "luxurywatch.com",
        "transactionLocation": "Miami, Florida",
    },
    {
        "userName": "Mike",
        "securityQuestion": "What is your favorite movie?",
        "securityAnswer": "Inception",
        "cardEnding": "3456",
        "transactionAmount": "$2,150.00",
        "transactionName": "GlobalTravel Agency",
        "transactionTime": "November 26, 2025 at 6:15 PM",
        "transactionCategory": "Travel",
        "transactionSource": "globaltravel.com",
        "transactionLocation": "Los Angeles, California",
    },
]


def seed_database():
    """Insert sample fraud cases"""
    # Initialize database (creates table if not exists)
    init_database()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM fraud_cases")

    # Insert each case
    for case in FRAUD_CASES:
        cursor.execute(
            """
            INSERT INTO fraud_cases 
            (userName, securityQuestion, securityAnswer, cardEnding, 
             transactionAmount, transactionName, transactionTime,
             transactionCategory, transactionSource, transactionLocation,
             status, createdAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending_review', ?)
        """,
            (
                case["userName"],
                case["securityQuestion"],
                case["securityAnswer"],
                case["cardEnding"],
                case["transactionAmount"],
                case["transactionName"],
                case["transactionTime"],
                case["transactionCategory"],
                case["transactionSource"],
                case["transactionLocation"],
                datetime.now().isoformat(),
            ),
        )

    conn.commit()
    conn.close()

    print(f"✅ Seeded {len(FRAUD_CASES)} fraud cases!")

    # Print all cases for verification
    print("\n📋 Current fraud cases:")
    for case in get_all_cases():
        print(
            f"   - ID: {case['id']}, User: {case['userName']}, "
            f"Card: ****{case['cardEnding']}, Status: {case['status']}"
        )


if __name__ == "__main__":
    seed_database()
