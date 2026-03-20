"""Seed script - initializes the database with mock data via the sync API."""

import asyncio
import httpx

API_BASE = "http://localhost:8000/api/v1"


async def seed():
    async with httpx.AsyncClient(timeout=30) as client:
        print("Checking API health...")
        r = await client.get(f"{API_BASE}/health")
        print(f"  Status: {r.json()}")

        print("\nRunning full sync (ingesting mock data)...")
        r = await client.post(f"{API_BASE}/sync/full")
        result = r.json()
        for key, value in result.items():
            print(f"  {key}: {value}")

        print("\nVerifying users...")
        r = await client.get(f"{API_BASE}/users")
        users = r.json()
        print(f"  Found {len(users)} users")

        for user in users[:3]:
            print(f"\n  --- {user['display_name']} ({user['employee_id']}) ---")
            print(f"      Dept: {user['department']}, State: {user['lifecycle_state']}")

            # Get comparison
            r = await client.get(f"{API_BASE}/comparison/{user['id']}")
            if r.status_code == 200:
                comp = r.json()
                print(f"      Compliance: {comp['overall_compliance_score']:.0%}")
                print(f"      Missing: {len(comp['missing_entitlements'])}, Excess: {len(comp['excess_entitlements'])}")

        print("\nTesting chat interface...")
        queries = [
            "Why does Sarah not have Epic access?",
            "Compare David Kim's access to his expected baseline.",
            "Recommend cleanup for Bob External.",
        ]
        for q in queries:
            print(f"\n  Q: {q}")
            r = await client.post(f"{API_BASE}/chat", json={"message": q})
            if r.status_code == 200:
                resp = r.json()
                answer = resp["answer"]
                if len(answer) > 200:
                    answer = answer[:200] + "..."
                print(f"  A: {answer}")
                print(f"     Intent: {resp['intent']}, Risk: {resp.get('risk_level', 'N/A')}")

        print("\nSeed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
