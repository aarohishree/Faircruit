"""
Seed jobs with professional rubrics and Gemini-powered questions
"""
import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv
from rubrics.professional_rubrics import ProfessionalRubrics
from loguru import logger

load_dotenv()

MONGO_URL = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "faircruit_db")
client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

async def seed_jobs_with_rubrics():
    """Create jobs with professional rubrics and Gemini-generated questions"""
    
    try:
        # Clear existing jobs
        await db.jobs.delete_many({})
        await db.rubrics.delete_many({})
        logger.info("Cleared existing jobs and rubrics")
        
        # Get or create recruiter
        recruiter = await db.users.find_one({"role": "recruiter"})
        if not recruiter:
            recruiter_id = ObjectId()
            recruiter = {
                "_id": recruiter_id,
                "email": "recruiter@example.com",
                "username": "recruiter",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUaIv9m6",
                "role": "recruiter",
                "company_id": str(recruiter_id),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await db.users.insert_one(recruiter)
            logger.info(f"✓ Created recruiter: {recruiter['email']}")
        else:
            logger.info(f"✓ Using existing recruiter: {recruiter['email']}")
        
        recruiter_id = str(recruiter["_id"])
        
        # Define jobs with their roles
        job_definitions = [
            {
                "title": "Senior Python Developer",
                "description": "We are looking for an experienced Python developer with expertise in async programming, testing, and code quality. You will work on scalable backend systems, design robust APIs, and mentor junior developers.",
                "role": "Software Engineer",
                "competencies": ["Technical Excellence", "System Design & Architecture", "Professionalism & Collaboration", "Engineering Leadership & Influence"]
            },
            {
                "title": "Full-Stack Web Developer",
                "description": "Looking for a full-stack developer proficient in React, Node.js, and database design. You'll build user-facing applications, design systems, and drive technical excellence across teams.",
                "role": "Software Engineer",
                "competencies": ["Technical Excellence", "System Design & Architecture", "Professionalism & Collaboration", "Engineering Leadership & Influence"]
            },
            {
                "title": "Data Scientist",
                "description": "Seeking a data scientist to build ML models and provide insights from complex datasets. You will design data pipelines, create predictive models, and present findings to stakeholders.",
                "role": "Data Scientist",
                "competencies": ["Technical Excellence", "System Design & Architecture", "Professionalism & Collaboration", "Engineering Leadership & Influence"]
            }
        ]
        
        # Get rubrics for Software Engineer
        se_rubrics = ProfessionalRubrics.software_engineer()
        logger.info(f"✓ Loaded {len(se_rubrics)} Professional Rubrics for Software Engineer")
        
        # Insert rubrics to DB
        rubric_ids = []
        for rubric in se_rubrics:
            rubric_dict = {
                "rubric_id": rubric.rubric_id,
                "role_name": rubric.role_name,
                "skill_name": rubric.skill_name,
                "descriptors": [
                    {
                        "level": d.level.value if hasattr(d.level, 'value') else str(d.level),
                        "description": d.description,
                        "criteria": d.criteria,
                        "weight": d.weight
                    }
                    for d in rubric.descriptors
                ],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = await db.rubrics.insert_one(rubric_dict)
            rubric_ids.append(str(result.inserted_id))
        
        logger.info(f"✓ Inserted {len(rubric_ids)} rubrics to database")
        
        # Create jobs (questions will be generated on-the-fly when applicant starts test)
        created_jobs = []
        for job_def in job_definitions:
            try:
                logger.info(f"\n📋 Processing: {job_def['title']}")
                
                # Create job document without questions (generated per-user)
                # Using schema-compliant structure
                job_doc = {
                    "title": job_def['title'],
                    "description": job_def['description'],
                    "competencies": [
                        {"level": "ANALYSIS", "description": skill, "evidence_type": "assessment"}
                        for skill in job_def['competencies']
                    ],
                    "evidence_types": ["mcq", "short_answer", "essay", "code_debug"],
                    "duration_minutes": 45,
                    "criteria": "Competency assessment based on professional rubrics",
                    "company_id": recruiter_id,
                    "poster_id": recruiter_id,
                    "status": "open",
                    "rubric_ids": rubric_ids,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = await db.jobs.insert_one(job_doc)
                created_jobs.append(job_def['title'])
                logger.info(f"  ✅ Job created with ID: {result.inserted_id}")
                
            except Exception as e:
                logger.error(f"  ❌ Error creating job '{job_def['title']}': {e}")
        
        logger.info(f"\n✅ Successfully created {len(created_jobs)} jobs with rubrics and Gemini questions:")
        for job_title in created_jobs:
            print(f"  ✓ {job_title}")
        
        logger.info("\nDatabase is ready for testing!")
        logger.info("Test credentials:")
        logger.info(f"  Recruiter: recruiter@example.com / password")
        logger.info(f"  Applicant: applicant@example.com / password")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_jobs_with_rubrics())
