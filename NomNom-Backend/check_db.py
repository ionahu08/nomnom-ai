#!/usr/bin/env python3
"""Quick database diagnostic script."""

import asyncio
from sqlalchemy import inspect, text
from src.database import engine
from src.models.user import Base

async def check_database():
    print("🔍 NomNom Database Diagnostic\n")

    try:
        # Test connection
        print("1️⃣  Testing database connection...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!\n")

        # Check tables
        print("2️⃣  Checking if tables exist...")
        async with engine.begin() as conn:
            inspector = inspect(conn.sync_engine)
            tables = inspector.get_table_names()

            if not tables:
                print("❌ No tables found in database")
                print("   Need to run: alembic upgrade head\n")
                return False

            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
            print()

        # Check specific tables needed for profiles
        print("3️⃣  Checking required tables...")
        required_tables = ['users', 'user_profiles']
        async with engine.begin() as conn:
            inspector = inspect(conn.sync_engine)
            existing_tables = inspector.get_table_names()

            missing = [t for t in required_tables if t not in existing_tables]
            if missing:
                print(f"❌ Missing tables: {missing}")
                print("   Run: alembic upgrade head\n")
                return False

            print("✅ All required tables exist!\n")

        # Check user_profiles columns
        print("4️⃣  Checking user_profiles columns...")
        async with engine.begin() as conn:
            inspector = inspect(conn.sync_engine)
            columns = inspector.get_columns('user_profiles')
            col_names = [c['name'] for c in columns]

            print(f"✅ Found {len(columns)} columns:")
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")

            # Check for new health profile columns
            health_cols = ['race', 'goal', 'medical_conditions', 'surgeries', 'medications']
            missing_health = [c for c in health_cols if c not in col_names]

            if missing_health:
                print(f"\n⚠️  Missing health profile columns: {missing_health}")
                print("   Run: alembic upgrade head\n")
                return False
            else:
                print(f"\n✅ All health profile columns present!\n")

        # Check if any users exist
        print("5️⃣  Checking user data...")
        from sqlalchemy import select
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) as count FROM users"))
            row = result.first()
            user_count = row[0] if row else 0
            print(f"✅ Users in database: {user_count}")

            if user_count > 0:
                result = await conn.execute(text("SELECT COUNT(*) as count FROM user_profiles WHERE user_id IS NOT NULL"))
                row = result.first()
                profile_count = row[0] if row else 0
                print(f"✅ User profiles: {profile_count}\n")
            else:
                print("   (No users created yet - normal for first run)\n")

        print("=" * 50)
        print("✅ DATABASE STATUS: READY")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        print("Database is NOT accessible!")
        print("\nPossible solutions:")
        print("1. Is PostgreSQL running? (brew services start postgresql)")
        print("2. Does database 'nomnom' exist? (createdb nomnom)")
        print("3. Run migrations: alembic upgrade head")
        print("4. Check .env file for correct DATABASE_URL")
        return False

if __name__ == "__main__":
    result = asyncio.run(check_database())
    exit(0 if result else 1)
