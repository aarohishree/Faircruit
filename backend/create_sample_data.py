"""
Script to create sample data for Faircruit testing
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
db = client["faircruit"]

async def create_sample_data():
    """Create sample users, jobs, and applications"""
    
    try:
        # Clear existing data
        print("Clearing existing collections...")
        await db.users.delete_many({})
        await db.jobs.delete_many({})
        
        # Create sample recruiter user
        recruiter_id = ObjectId()
        recruiter = {
            "_id": recruiter_id,
            "email": "recruiter@example.com",
            "username": "recruiter",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaIv9m6",  # "password"
            "role": "recruiter",
            "company_id": str(recruiter_id),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await db.users.insert_one(recruiter)
        print(f"✓ Created recruiter: {recruiter['email']}")
        
        # Create sample applicant user
        applicant_id = ObjectId()
        applicant = {
            "_id": applicant_id,
            "email": "applicant@example.com",
            "username": "applicant",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaIv9m6",  # "password"
            "role": "applicant",
            "company_id": str(recruiter_id),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await db.users.insert_one(applicant)
        print(f"✓ Created applicant: {applicant['email']}")
        
        # Create sample jobs with 4 competencies (matching 4 rubrics)
        jobs = [
            {
                "title": "Senior Python Developer",
                "description": "We are looking for an experienced Python developer with expertise in async programming, testing, and code quality.",
                "company_id": str(recruiter_id),
                "poster_id": str(recruiter_id),
                "competencies": [
                    "Problem Solving",
                    "Technical Communication",
                    "System Design",
                    "Leadership & Mentoring"
                ],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "open"
            },
            {
                "title": "Full-Stack Web Developer",
                "description": "Looking for a full-stack developer proficient in React, Node.js, and database design.",
                "company_id": str(recruiter_id),
                "poster_id": str(recruiter_id),
                "competencies": [
                    "Web Development",
                    "User Experience Design",
                    "Database Management",
                    "Team Leadership"
                ],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "open"
            },
            {
                "title": "Data Scientist",
                "description": "Seeking a data scientist to build ML models and provide insights from complex datasets.",
                "company_id": str(recruiter_id),
                "poster_id": str(recruiter_id),
                "competencies": [
                    "Statistical Analysis",
                    "Machine Learning",
                    "Data Communication",
                    "Research Leadership"
                ],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "open"
            }
        ]
        
        result = await db.jobs.insert_many(jobs)
        print(f"✓ Created {len(jobs)} sample jobs:")
        for i, job in enumerate(jobs):
            print(f"  - {job['title']}")
        
        print("\n✅ Sample data created successfully!")
        print(f"\nCredentials for testing:")
        print(f"  Recruiter: recruiter@example.com / password")
        print(f"  Applicant: applicant@example.com / password")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_sample_data())
