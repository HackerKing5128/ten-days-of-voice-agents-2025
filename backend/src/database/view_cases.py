"""
Simple script to view all fraud cases in the database.
Run with: uv run python -m src.database.view_cases
"""

from .fraud_db import get_all_cases

def view_all_cases():
    cases = get_all_cases()
    
    print("\n" + "="*70)
    print("🏦 SECUREBANK FRAUD CASES DATABASE")
    print("="*70 + "\n")
    
    if not cases:
        print("No cases found in database.")
        return
    
    for case in cases:
        status = case['status']
        
        # Status emoji
        if status == 'pending_review':
            status_icon = "⏳"
            status_color = "PENDING"
        elif status == 'confirmed_safe':
            status_icon = "✅"
            status_color = "SAFE"
        elif status == 'confirmed_fraud':
            status_icon = "🚨"
            status_color = "FRAUD"
        elif status == 'verification_failed':
            status_icon = "❌"
            status_color = "FAILED"
        else:
            status_icon = "❓"
            status_color = status
        
        print(f"┌{'─'*68}┐")
        print(f"│ Case #{case['id']}: {case['userName']:<20} {status_icon} {status_color:>30} │")
        print(f"├{'─'*68}┤")
        print(f"│ Card: ****{case['cardEnding']:<10} Amount: {case['transactionAmount']:<20} │")
        print(f"│ Merchant: {case['transactionName']:<50} │")
        print(f"│ Location: {case['transactionLocation']:<50} │")
        print(f"│ Time: {case['transactionTime']:<54} │")
        
        if case.get('outcomeNote'):
            print(f"├{'─'*68}┤")
            print(f"│ Note: {case['outcomeNote']:<54} │")
        
        if case.get('updatedAt'):
            print(f"│ Updated: {case['updatedAt']:<51} │")
        
        print(f"└{'─'*68}┘")
        print()
    
    print("="*70 + "\n")


if __name__ == "__main__":
    view_all_cases()
