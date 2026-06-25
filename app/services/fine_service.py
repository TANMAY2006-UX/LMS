from app.extensions import db
from app.models.transaction import Transaction, Fine, FinePolicy
from app.models.user import User
from datetime import datetime, date, timedelta

class FineService:
    """
    Handles the calculation, payment, and waiving of library fines.
    """

    @staticmethod
    def calculate_fine(transaction_id: int):
        """
        Triggered automatically when a book is returned.
        Calculates overdue days, applies tier policies, and creates a Fine record if necessary.
        """
        txn = Transaction.query.get(transaction_id)
        if not txn or not txn.returned_at:
            print(f"[FINE] Txn {transaction_id} not found or not returned.")
            return {"success": False, "error": "Transaction not found or not yet returned."}

        # 1. Check if it's actually late
        returned_date = txn.returned_at.date()
        if returned_date <= txn.due_date:
            print(f"[FINE] Txn {transaction_id} returned on time. No fine.")
            return {"success": True, "message": "Returned on time. No fine."}

        # 2. Get the member's specific policy (e.g., student vs faculty)
        member = User.query.get(txn.member_id)
        policy = FinePolicy.query.filter_by(applies_to_tier=member.tier, is_active=True).first()
        
        # Fallback to a default policy if tier-specific is missing
        if not policy:
            policy = FinePolicy.query.filter_by(applies_to_tier='default', is_active=True).first()
            
        if not policy:
            # If absolutely no policies exist, we cannot calculate a fine
            print(f"[FINE] ABORTED: No fine policy found for tier '{member.tier}' or 'default'.")
            return {"success": False, "error": "No active fine policy found in the system."}

        # 3. Calculate Raw Overdue Days
        raw_days_overdue = (returned_date - txn.due_date).days
        billable_days = raw_days_overdue

        # 4. Handle Weekend Exclusions (if policy dictates)
        if policy.exclude_weekends:
            billable_days = 0
            current_date = txn.due_date + timedelta(days=1)
            while current_date <= returned_date:
                if current_date.weekday() < 5: # 0-4 are Monday-Friday
                    billable_days += 1
                current_date += timedelta(days=1)

        # 5. Apply Grace Period
        billable_days -= policy.grace_days
        
        if billable_days <= 0:
            print(f"[FINE] Txn {transaction_id} covered by grace period. No fine.")
            return {"success": True, "message": "Returned within grace period. No fine."}

        # 6. Calculate Amount & Apply Caps
        fine_amount = billable_days * policy.rate_per_day
        if policy.max_fine_cap and fine_amount > policy.max_fine_cap:
            fine_amount = policy.max_fine_cap


        print(f"[FINE] Calculated fine: ₹{fine_amount} for {billable_days} billable days.")
        # 7. Create the Fine Record in the DB
        try:
            fine = Fine(
                transaction_id=txn.id,
                amount=fine_amount,
                days_overdue=raw_days_overdue,
                status='pending'
            )
            db.session.add(fine)
            db.session.commit()
            print(f"[FINE] Successfully saved pending fine #{fine.id}.")
            return {"success": True, "fine": fine}
            
        except Exception as e:
            db.session.rollback()
            print(f"[FINE] Database error saving fine: {e}")
            return {"success": False, "error": f"Failed to save fine: {str(e)}"}