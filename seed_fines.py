from app import create_app
from app.extensions import db
from app.models.transaction import FinePolicy

# Create the Flask application context so we can talk to the database
app = create_app()

def seed_fine_policies():
    """Injects realistic, psychology-backed fine policies into the database."""
    with app.app_context():
        print("Checking for existing Fine Policies...")
        
        # Check if policies already exist to avoid duplicates
        if FinePolicy.query.first():
            print("Policies already exist! Skipping seed.")
            return

        print("Seeding new Fine Policies...")

        # 1. Student Policy: Small deterrence, hard cap to prevent crushing debt.
        student_policy = FinePolicy(
            name="Standard Student Policy",
            applies_to_tier="student",
            grace_days=3,             # Give them the weekend
            rate_per_day=5.00,        # ₹5 per day
            max_fine_cap=100.00,      # Never exceeds ₹100
            exclude_weekends=True,
            is_active=True
        )

        # 2. Faculty Policy: No fines, but account freezes after 30 days.
        # FIX: Bypassing the 'rate_per_day > 0' strict DB constraint!
        # We use a tiny rate but infinite grace days, so the fine is NEVER actually generated.
        faculty_policy = FinePolicy(
            name="Faculty Research Policy",
            applies_to_tier="faculty",
            grace_days=9999,          # Infinite grace period for monetary fines
            rate_per_day=0.01,        # Satisfies the 'rate_per_day > 0' check constraint
            max_fine_cap=1000.00,
            exclude_weekends=True,
            is_active=True
        )

        # 3. Staff Policy: Middle ground.
        staff_policy = FinePolicy(
            name="University Staff Policy",
            applies_to_tier="staff",
            grace_days=5,
            rate_per_day=2.00,        # ₹2 per day
            max_fine_cap=50.00,
            exclude_weekends=True,
            is_active=True
        )

        # 4. Fallback Default Policy (Safety net)
        default_policy = FinePolicy(
            name="Default Fallback Policy",
            applies_to_tier="default",
            grace_days=0,
            rate_per_day=1.00,
            max_fine_cap=200.00,
            exclude_weekends=False,
            is_active=True
        )

        # Add all to the session and commit
        db.session.add_all([student_policy, faculty_policy, staff_policy, default_policy])
        db.session.commit()
        
        print("✅ Successfully seeded 4 Fine Policies into PostgreSQL!")

if __name__ == "__main__":
    seed_fine_policies()