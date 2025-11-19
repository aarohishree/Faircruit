import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv

async def check_users():
    mongo_uri = getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = getenv("DB_NAME", "faircruit_db")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    users_col = db['users']
    
    applicant = await users_col.find_one({"email": "applicant@example.com"})
    if applicant:
        print("✓ Applicant document fields:")
        for key in applicant.keys():
            print(f"  - {key}")
        print(f"\nPassword hash value (first 50 chars): {str(applicant.get('hashed_password', 'MISSING'))[:50]}")

asyncio.run(check_users())
