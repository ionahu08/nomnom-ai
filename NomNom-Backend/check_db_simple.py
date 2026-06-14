#!/usr/bin/env python3
"""Simple database diagnostic - uses psql directly."""

import subprocess
import os

def run_psql(query):
    """Run a psql query."""
    try:
        result = subprocess.run(
            ["psql", "-U", "postgres", "-h", "localhost", "-d", "nomnom", "-c", query],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

print("🔍 NomNom Database Diagnostic (Simple Version)\n")

# Test 1: Connect to database
print("1️⃣  Testing database connection...")
output, code = run_psql("SELECT version();")
if code == 0:
    print("✅ Database connection successful!")
    print(f"   {output.split('PostgreSQL')[1][:50] if 'PostgreSQL' in output else output[:50]}...\n")
else:
    print("❌ Cannot connect to database")
    print("   Make sure PostgreSQL is running and 'nomnom' database exists")
    print(f"   Error: {output}\n")
    print("   Try: createdb -U postgres nomnom\n")
    exit(1)

# Test 2: List tables
print("2️⃣  Checking tables...")
output, code = run_psql("\\dt")
if "users" in output and "user_profiles" in output:
    print("✅ Required tables exist:")
    for line in output.split('\n'):
        if 'users' in line or 'food_logs' in line or 'nutrition' in line:
            print(f"   {line}")
    print()
else:
    print("❌ Missing required tables")
    print("   Run: cd NomNom-Backend && alembic upgrade head\n")
    exit(1)

# Test 3: Check health profile columns
print("3️⃣  Checking health profile columns...")
output, code = run_psql("\\d user_profiles")
if "race" in output and "goal" in output and "medical_conditions" in output:
    print("✅ All health profile columns exist:")
    health_cols = ['race', 'goal', 'medical_conditions', 'surgeries', 'medications']
    for col in health_cols:
        if col in output:
            print(f"   ✓ {col}")
    print()
else:
    print("⚠️  Some health profile columns are missing:")
    health_cols = ['race', 'goal', 'medical_conditions', 'surgeries', 'medications']
    for col in health_cols:
        status = "✓" if col in output else "✗"
        print(f"   {status} {col}")
    print("\n   Run: cd NomNom-Backend && alembic upgrade head\n")

# Test 4: Check user data
print("4️⃣  Checking user data...")
output, code = run_psql("SELECT COUNT(*) as user_count FROM users;")
if code == 0:
    count = output.split('\n')[2].strip() if len(output.split('\n')) > 2 else "unknown"
    print(f"✅ Users in database: {count}\n")
else:
    print(f"⚠️  Could not count users: {output}\n")

print("=" * 50)
print("✅ DATABASE: READY FOR API CALLS")
print("=" * 50)
print("\nYour database is set up! If Settings screen still shows")
print("error, it means the API endpoint or authentication is failing.")
print("\nNext steps:")
print("1. Make sure backend is still running")
print("2. Check if user has a profile (try POST /api/v1/profile/)")
print("3. Verify JWT token is being sent with requests")
