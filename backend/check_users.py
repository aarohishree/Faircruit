import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv

async def check_users():
    mongo_uri = getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = getenv("DB_NAME", "faircruit_db")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    users_col = db['users']
    
    user_list = await users_col.find().to_list(None)
    print(f'\n✓ Total users in DB: {len(user_list)}')
    for user in user_list:
        print(f'  - Email: {user.get("email")}, Role: {user.get("role")}')
    
    # Check specific user
    print("\n✓ Looking for applicant@example.com...")
    applicant = await users_col.find_one({"email": "applicant@example.com"})
    if applicant:
        print(f"  Found! Password hash exists: {'password_hash' in applicant}")
    else:
        print("  NOT FOUND - This is the problem!")

asyncio.run(check_users())
