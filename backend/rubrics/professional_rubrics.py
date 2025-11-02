"""
Professional Rubrics for 10 Real-World Job Roles
Designed for actual hiring and competency assessment systems
"""
import uuid
from models.schemas import CompetencyLevel, RubricDescriptor, Rubric
from typing import List


class ProfessionalRubrics:
    """Collection of production-ready rubrics for common job roles"""

    @staticmethod
    def software_engineer() -> Rubric:
        """Rubric for Software Engineer positions"""
        descriptors = [
            RubricDescriptor(
                level=CompetencyLevel.AWARENESS,
                description="Understands programming fundamentals and can write basic code with supervision.",
                keywords=["syntax", "variables", "loops", "functions", "debugging basics", "git basics"],
                criteria=[
                    "Writes syntactically correct code in at least one language",
                    "Understands basic data structures (arrays, lists, dictionaries)",
                    "Can fix simple bugs with guidance",
                    "Familiar with version control concepts",
                    "Requires detailed instructions for tasks"
                ],
                weight=0.8,
                expected_experience="0-1 years or student",
                expected_projects="1-3 academic/personal projects",
                expected_skills=["One programming language", "Basic algorithms", "Version control basics"],
                expected_achievements=["Completed coursework", "Basic certifications", "Personal projects"]
            ),
            RubricDescriptor(
                level=CompetencyLevel.APPLICATION,
                description="Independently implements features and fixes bugs in existing codebases.",
                keywords=["implement", "debug", "test", "code review", "API", "database queries"],
                criteria=[
                    "Implements features from specifications independently",
                    "Writes unit tests for own code",
                    "Debugs issues without constant supervision",
                    "Participates effectively in code reviews",
                    "Works with APIs and databases competently",
                    "Follows team coding standards and best practices"
                ],
                weight=1.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.ANALYSIS,
                description="Designs technical solutions and makes architectural decisions for components.",
                keywords=["design patterns", "performance", "scalability", "trade-offs", "architecture"],
                criteria=[
                    "Designs solutions for complex technical problems",
                    "Identifies and resolves performance bottlenecks",
                    "Applies appropriate design patterns",
                    "Evaluates trade-offs in technical decisions",
                    "Conducts thorough technical investigations",
                    "Proposes improvements to existing systems"
                ],
                weight=1.2
            ),
            RubricDescriptor(
                level=CompetencyLevel.SYNTHESIS,
                description="Architects large-scale systems and creates innovative technical solutions.",
                keywords=["architect", "distributed systems", "microservices", "system design", "innovation"],
                criteria=[
                    "Architects scalable distributed systems",
                    "Designs systems handling millions of users",
                    "Creates reusable frameworks and libraries",
                    "Integrates multiple technologies effectively",
                    "Drives technical strategy for major projects",
                    "Innovates solutions to novel problems"
                ],
                weight=1.5
            ),
            RubricDescriptor(
                level=CompetencyLevel.MASTERY,
                description="Technical authority with deep expertise across multiple domains.",
                keywords=["expert", "thought leader", "optimize", "cutting-edge", "technical authority"],
                criteria=[
                    "Recognized as go-to expert in multiple areas",
                    "Solves the most complex technical challenges",
                    "Masters multiple technology stacks and paradigms",
                    "Optimizes systems at massive scale",
                    "Sets technical standards for organization",
                    "Contributes to open source or publishes technical content"
                ],
                weight=2.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.INFLUENCE,
                description="Industry thought leader who shapes technical direction and mentors senior engineers.",
                keywords=["thought leader", "strategy", "mentor", "industry impact", "evangelist"],
                criteria=[
                    "Influences organizational and industry technical direction",
                    "Mentors and develops senior engineers and architects",
                    "Speaks at major conferences and events",
                    "Publishes influential technical content",
                    "Drives adoption of best practices industry-wide",
                    "Recognized expert with significant external reputation"
                ],
                weight=2.5
            )
        ]

        return Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Software Engineer",
            skill_name="Software Development",
            descriptors=descriptors
        )

    @staticmethod
    def data_scientist() -> Rubric:
        """Rubric for Data Scientist positions"""
        descriptors = [
            RubricDescriptor(
                level=CompetencyLevel.AWARENESS,
                description="Understands basic statistics and can perform simple data analysis.",
                keywords=["statistics", "pandas", "visualization", "SQL", "data exploration"],
                criteria=[
                    "Understands basic statistical concepts",
                    "Can query databases using SQL",
                    "Creates basic visualizations",
                    "Performs exploratory data analysis with guidance",
                    "Familiar with Python/R for data analysis"
                ],
                weight=0.8
            ),
            RubricDescriptor(
                level=CompetencyLevel.APPLICATION,
                description="Builds and deploys machine learning models to solve business problems.",
                keywords=["ML models", "feature engineering", "model evaluation", "deployment", "scikit-learn"],
                criteria=[
                    "Builds supervised/unsupervised ML models",
                    "Performs feature engineering and selection",
                    "Evaluates models using appropriate metrics",
                    "Deploys models to production environments",
                    "Communicates findings to stakeholders",
                    "Handles data preprocessing and cleaning"
                ],
                weight=1.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.ANALYSIS,
                description="Designs experiments and selects optimal modeling approaches for complex problems.",
                keywords=["A/B testing", "experimental design", "model selection", "causal inference"],
                criteria=[
                    "Designs robust experiments and A/B tests",
                    "Selects appropriate algorithms for problem domains",
                    "Performs causal inference and impact analysis",
                    "Optimizes model performance systematically",
                    "Identifies and mitigates bias in models",
                    "Analyzes business metrics and KPIs"
                ],
                weight=1.2
            ),
            RubricDescriptor(
                level=CompetencyLevel.SYNTHESIS,
                description="Develops novel ML solutions and builds end-to-end data platforms.",
                keywords=["deep learning", "ML infrastructure", "research", "novel algorithms"],
                criteria=[
                    "Develops custom ML algorithms and approaches",
                    "Builds scalable ML infrastructure and pipelines",
                    "Integrates multiple data sources and models",
                    "Applies cutting-edge research to business problems",
                    "Creates reusable ML frameworks",
                    "Designs comprehensive data strategies"
                ],
                weight=1.5
            ),
            RubricDescriptor(
                level=CompetencyLevel.MASTERY,
                description="ML expert driving innovation and setting data science standards.",
                keywords=["ML research", "state-of-the-art", "patents", "ML leadership"],
                criteria=[
                    "Recognized expert in specialized ML domains",
                    "Publishes research papers or patents",
                    "Develops state-of-the-art models",
                    "Sets ML best practices and standards",
                    "Solves previously unsolved ML challenges",
                    "Masters multiple ML paradigms"
                ],
                weight=2.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.INFLUENCE,
                description="Data science thought leader shaping industry practices.",
                keywords=["data strategy", "ML evangelist", "industry leader", "keynote speaker"],
                criteria=[
                    "Shapes organizational data and ML strategy",
                    "Keynote speaker at major ML conferences",
                    "Mentors senior data scientists",
                    "Influences industry ML practices",
                    "Strong external reputation in data science",
                    "Drives ML adoption at scale"
                ],
                weight=2.5
            )
        ]

        return Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Data Scientist",
            skill_name="Machine Learning & Data Science",
            descriptors=descriptors
        )

    @staticmethod
    def product_manager() -> Rubric:
        """Rubric for Product Manager positions"""
        descriptors = [
            RubricDescriptor(
                level=CompetencyLevel.AWARENESS,
                description="Understands product development basics and can support product initiatives.",
                keywords=["user stories", "roadmap", "stakeholders", "requirements", "agile basics"],
                criteria=[
                    "Writes clear user stories and requirements",
                    "Understands agile development process",
                    "Gathers basic user feedback",
                    "Supports product launches with guidance",
                    "Communicates with engineering teams"
                ],
                weight=0.8
            ),
            RubricDescriptor(
                level=CompetencyLevel.APPLICATION,
                description="Manages product features and coordinates cross-functional delivery.",
                keywords=["feature prioritization", "sprint planning", "metrics", "user research"],
                criteria=[
                    "Prioritizes features using data and frameworks",
                    "Runs sprint planning and grooming sessions",
                    "Defines and tracks product metrics",
                    "Conducts user research and interviews",
                    "Manages product backlog effectively",
                    "Coordinates cross-functional teams"
                ],
                weight=1.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.ANALYSIS,
                description="Drives product strategy and makes data-driven product decisions.",
                keywords=["product strategy", "market analysis", "competitive analysis", "OKRs"],
                criteria=[
                    "Develops product strategy and roadmap",
                    "Conducts thorough market and competitive analysis",
                    "Makes trade-off decisions using data",
                    "Sets and tracks OKRs and KPIs",
                    "Identifies and validates opportunities",
                    "Analyzes user behavior and trends"
                ],
                weight=1.2
            ),
            RubricDescriptor(
                level=CompetencyLevel.SYNTHESIS,
                description="Creates innovative products and builds new product lines.",
                keywords=["product vision", "0-to-1", "innovation", "go-to-market"],
                criteria=[
                    "Builds products from 0-to-1",
                    "Creates compelling product vision",
                    "Drives product innovation",
                    "Develops go-to-market strategies",
                    "Integrates multiple product areas",
                    "Launches successful new product lines"
                ],
                weight=1.5
            ),
            RubricDescriptor(
                level=CompetencyLevel.MASTERY,
                description="Product leader with proven track record of successful products.",
                keywords=["product leadership", "portfolio", "revenue impact", "transformation"],
                criteria=[
                    "Manages multiple products or large product area",
                    "Proven track record of successful launches",
                    "Drives significant revenue or user growth",
                    "Transforms product organization",
                    "Recognized product expert in domain",
                    "Builds and mentors product teams"
                ],
                weight=2.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.INFLUENCE,
                description="Product visionary shaping industry and organizational direction.",
                keywords=["product vision", "industry impact", "thought leadership", "CPO-level"],
                criteria=[
                    "Sets product vision for entire organization",
                    "Influences industry product practices",
                    "Speaks at major product conferences",
                    "Mentors senior product leaders",
                    "Drives company-wide transformation",
                    "Strong external reputation in product"
                ],
                weight=2.5
            )
        ]

        return Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Product Manager",
            skill_name="Product Management",
            descriptors=descriptors
        )

    @staticmethod
    def devops_engineer() -> Rubric:
        """Rubric for DevOps/SRE Engineer positions"""
        descriptors = [
            RubricDescriptor(
                level=CompetencyLevel.AWARENESS,
                description="Understands CI/CD basics and can perform routine operational tasks.",
                keywords=["CI/CD", "docker", "monitoring", "scripting", "linux basics"],
                criteria=[
                    "Understands containerization basics",
                    "Can write basic automation scripts",
                    "Familiar with CI/CD concepts",
                    "Monitors system health and alerts",
                    "Performs routine deployments with guidance"
                ],
                weight=0.8
            ),
            RubricDescriptor(
                level=CompetencyLevel.APPLICATION,
                description="Builds and maintains CI/CD pipelines and infrastructure.",
                keywords=["kubernetes", "terraform", "ansible", "AWS/Azure/GCP", "automation"],
                criteria=[
                    "Builds and maintains CI/CD pipelines",
                    "Manages infrastructure as code",
                    "Deploys and manages containerized applications",
                    "Automates repetitive operational tasks",
                    "Responds to and resolves incidents",
                    "Implements monitoring and alerting"
                ],
                weight=1.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.ANALYSIS,
                description="Designs reliable infrastructure and improves system performance.",
                keywords=["reliability", "performance tuning", "capacity planning", "SLI/SLO"],
                criteria=[
                    "Designs for high availability and reliability",
                    "Performs capacity planning and optimization",
                    "Defines and tracks SLIs/SLOs/SLAs",
                    "Conducts post-mortem analysis",
                    "Improves system observability",
                    "Identifies and eliminates bottlenecks"
                ],
                weight=1.2
            ),
            RubricDescriptor(
                level=CompetencyLevel.SYNTHESIS,
                description="Architects cloud infrastructure and platform solutions at scale.",
                keywords=["platform engineering", "multi-cloud", "architecture", "cost optimization"],
                criteria=[
                    "Architects multi-region cloud infrastructure",
                    "Builds internal platform and tooling",
                    "Designs disaster recovery strategies",
                    "Optimizes infrastructure costs significantly",
                    "Creates self-service platforms for developers",
                    "Integrates complex systems reliably"
                ],
                weight=1.5
            ),
            RubricDescriptor(
                level=CompetencyLevel.MASTERY,
                description="Infrastructure expert with deep knowledge of large-scale systems.",
                keywords=["site reliability", "chaos engineering", "large-scale", "expert"],
                criteria=[
                    "Manages infrastructure for massive scale",
                    "Implements chaos engineering practices",
                    "Expert in multiple cloud platforms",
                    "Achieves 99.99%+ uptime for critical systems",
                    "Sets infrastructure standards",
                    "Recognized expert in DevOps/SRE"
                ],
                weight=2.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.INFLUENCE,
                description="DevOps leader driving platform strategy and industry practices.",
                keywords=["platform strategy", "SRE culture", "industry leader", "transformation"],
                criteria=[
                    "Defines platform and infrastructure strategy",
                    "Transforms organizational DevOps culture",
                    "Influences industry SRE practices",
                    "Speaks at major infrastructure conferences",
                    "Mentors senior SRE/DevOps engineers",
                    "Drives adoption of reliability practices"
                ],
                weight=2.5
            )
        ]

        return Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="DevOps Engineer",
            skill_name="DevOps & Site Reliability",
            descriptors=descriptors
        )

    @staticmethod
    def ux_designer() -> Rubric:
        """Rubric for UX/UI Designer positions"""
        descriptors = [
            RubricDescriptor(
                level=CompetencyLevel.AWARENESS,
                description="Understands design principles and can create basic UI designs.",
                keywords=["wireframes", "mockups", "design tools", "user-centered", "visual design"],
                criteria=[
                    "Creates wireframes and mockups",
                    "Understands basic design principles",
                    "Uses design tools (Figma, Sketch, etc.)",
                    "Follows design systems and guidelines",
                    "Gathers basic user feedback"
                ],
                weight=0.8
            ),
            RubricDescriptor(
                level=CompetencyLevel.APPLICATION,
                description="Designs user interfaces and conducts usability research.",
                keywords=["user research", "prototyping", "usability testing", "design systems"],
                criteria=[
                    "Conducts user research and interviews",
                    "Creates interactive prototypes",
                    "Performs usability testing",
                    "Contributes to design systems",
                    "Designs responsive interfaces",
                    "Collaborates effectively with developers"
                ],
                weight=1.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.ANALYSIS,
                description="Leads design projects and makes strategic UX decisions.",
                keywords=["information architecture", "user flows", "analytics", "A/B testing"],
                criteria=[
                    "Designs complex user flows and journeys",
                    "Creates information architecture",
                    "Uses data and analytics to inform decisions",
                    "Leads A/B testing initiatives",
                    "Identifies and solves usability problems",
                    "Mentors junior designers"
                ],
                weight=1.2
            ),
            RubricDescriptor(
                level=CompetencyLevel.SYNTHESIS,
                description="Creates innovative design solutions and builds design systems.",
                keywords=["design strategy", "innovation", "design systems", "product vision"],
                criteria=[
                    "Develops design strategy and vision",
                    "Creates comprehensive design systems",
                    "Innovates new interaction patterns",
                    "Designs for multiple platforms",
                    "Influences product direction through design",
                    "Leads major design initiatives"
                ],
                weight=1.5
            ),
            RubricDescriptor(
                level=CompetencyLevel.MASTERY,
                description="Design expert recognized for excellence and innovation.",
                keywords=["design excellence", "awards", "design leadership", "portfolio"],
                criteria=[
                    "Portfolio of award-winning designs",
                    "Recognized expert in specialized domain",
                    "Sets design standards for organization",
                    "Drives design excellence",
                    "Masters multiple design disciplines",
                    "Significant impact on user experience"
                ],
                weight=2.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.INFLUENCE,
                description="Design leader shaping design culture and industry practices.",
                keywords=["design culture", "thought leader", "design transformation", "speaking"],
                criteria=[
                    "Shapes organizational design culture",
                    "Influences industry design practices",
                    "Speaks at major design conferences",
                    "Builds and leads design teams",
                    "Strong external design reputation",
                    "Mentors senior design leaders"
                ],
                weight=2.5
            )
        ]

        return Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="UX Designer",
            skill_name="User Experience Design",
            descriptors=descriptors
        )

    @staticmethod
    def security_engineer() -> Rubric:
        """Rubric for Security Engineer positions"""
        descriptors = [
            RubricDescriptor(
                level=CompetencyLevel.AWARENESS,
                description="Understands security basics and follows security best practices.",
                keywords=["security basics", "OWASP", "encryption", "authentication", "compliance"],
                criteria=[
                    "Understands common security vulnerabilities",
                    "Follows secure coding practices",
                    "Familiar with OWASP Top 10",
                    "Implements basic authentication/authorization",
                    "Understands encryption fundamentals"
                ],
                weight=0.8
            ),
            RubricDescriptor(
                level=CompetencyLevel.APPLICATION,
                description="Performs security assessments and implements security controls.",
                keywords=["penetration testing", "vulnerability scanning", "security controls", "incident response"],
                criteria=[
                    "Conducts security assessments and testing",
                    "Implements security controls and policies",
                    "Performs vulnerability scanning and remediation",
                    "Responds to security incidents",
                    "Manages security tools and systems",
                    "Conducts security code reviews"
                ],
                weight=1.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.ANALYSIS,
                description="Designs security architecture and analyzes complex threats.",
                keywords=["threat modeling", "security architecture", "risk assessment", "forensics"],
                criteria=[
                    "Designs security architecture and solutions",
                    "Performs threat modeling and risk assessment",
                    "Analyzes complex security incidents",
                    "Conducts digital forensics",
                    "Identifies and prioritizes security risks",
                    "Develops security strategies"
                ],
                weight=1.2
            ),
            RubricDescriptor(
                level=CompetencyLevel.SYNTHESIS,
                description="Builds comprehensive security programs and infrastructure.",
                keywords=["security program", "zero trust", "compliance", "automation"],
                criteria=[
                    "Builds comprehensive security programs",
                    "Architects zero-trust security models",
                    "Ensures regulatory compliance (SOC2, ISO, etc.)",
                    "Automates security operations",
                    "Integrates security across organization",
                    "Develops custom security tools"
                ],
                weight=1.5
            ),
            RubricDescriptor(
                level=CompetencyLevel.MASTERY,
                description="Security expert with specialized knowledge in advanced domains.",
                keywords=["security expert", "certifications", "advanced threats", "research"],
                criteria=[
                    "Expert in specialized security domains",
                    "Holds advanced certifications (CISSP, OSCP, etc.)",
                    "Researches and discovers vulnerabilities",
                    "Defends against advanced persistent threats",
                    "Sets security standards",
                    "Recognized security authority"
                ],
                weight=2.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.INFLUENCE,
                description="Security leader shaping security posture and industry practices.",
                keywords=["CISO-level", "security strategy", "industry leader", "transformation"],
                criteria=[
                    "Defines organizational security strategy",
                    "Influences industry security practices",
                    "Speaks at security conferences",
                    "Builds and leads security teams",
                    "Drives security culture transformation",
                    "Strong reputation in security community"
                ],
                weight=2.5
            )
        ]

        return Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Security Engineer",
            skill_name="Information Security",
            descriptors=descriptors
        )

    @staticmethod
    def business_analyst() -> Rubric:
        """Rubric for Business Analyst positions"""
        descriptors = [
            RubricDescriptor(
                level=CompetencyLevel.AWARENESS,
                description="Understands business processes and can gather requirements.",
                keywords=["requirements", "documentation", "stakeholders", "process mapping"],
                criteria=[
                    "Gathers and documents requirements",
                    "Creates process flow diagrams",
                    "Communicates with stakeholders",
                    "Understands business domain basics",
                    "Assists in data analysis"
                ],
                weight=0.8
            ),
            RubricDescriptor(
                level=CompetencyLevel.APPLICATION,
                description="Analyzes business processes and recommends improvements.",
                keywords=["process improvement", "data analysis", "business cases", "SQL"],
                criteria=[
                    "Analyzes business processes end-to-end",
                    "Performs data analysis using SQL and Excel",
                    "Creates business cases and ROI analysis",
                    "Recommends process improvements",
                    "Facilitates stakeholder workshops",
                    "Tracks and reports on metrics"
                ],
                weight=1.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.ANALYSIS,
                description="Drives business transformation and strategic initiatives.",
                keywords=["transformation", "strategic planning", "change management", "business strategy"],
                criteria=[
                    "Drives business transformation initiatives",
                    "Conducts strategic analysis and planning",
                    "Manages change management programs",
                    "Identifies strategic opportunities",
                    "Evaluates business trade-offs",
                    "Influences business strategy"
                ],
                weight=1.2
            ),
            RubricDescriptor(
                level=CompetencyLevel.SYNTHESIS,
                description="Designs innovative business solutions and frameworks.",
                keywords=["business innovation", "framework development", "optimization"],
                criteria=[
                    "Designs innovative business solutions",
                    "Creates frameworks and methodologies",
                    "Optimizes complex business operations",
                    "Integrates cross-functional processes",
                    "Leads large-scale initiatives",
                    "Develops business capabilities"
                ],
                weight=1.5
            ),
            RubricDescriptor(
                level=CompetencyLevel.MASTERY,
                description="Business expert driving organizational excellence.",
                keywords=["business expertise", "operational excellence", "transformation leader"],
                criteria=[
                    "Recognized expert in business domain",
                    "Drives operational excellence",
                    "Leads transformational programs",
                    "Significant business impact (revenue, cost)",
                    "Sets business analysis standards",
                    "Mentors senior analysts"
                ],
                weight=2.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.INFLUENCE,
                description="Business leader shaping organizational and industry direction.",
                keywords=["executive influence", "industry practices", "thought leadership"],
                criteria=[
                    "Influences executive decision-making",
                    "Shapes industry business practices",
                    "Speaks at business conferences",
                    "Builds and leads BA teams",
                    "Drives organization-wide transformation",
                    "Strong reputation in business analysis"
                ],
                weight=2.5
            )
        ]

        return Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Business Analyst",
            skill_name="Business Analysis",
            descriptors=descriptors
        )

    @staticmethod
    def marketing_manager() -> Rubric:
        """Rubric for Marketing Manager positions"""
        descriptors = [
            RubricDescriptor(
                level=CompetencyLevel.AWARENESS,
                description="Understands marketing basics and executes campaigns with guidance.",
                keywords=["campaigns", "content", "social media", "analytics", "SEO basics"],
                criteria=[
                    "Executes marketing campaigns",
                    "Creates marketing content",
                    "Manages social media accounts",
                    "Understands basic marketing metrics",
                    "Familiar with SEO and SEM concepts"
                ],
                weight=0.8
            ),
            RubricDescriptor(
                level=CompetencyLevel.APPLICATION,
                description="Plans and manages marketing campaigns across channels.",
                keywords=["campaign management", "budget", "analytics", "content strategy", "lead generation"],
                criteria=[
                    "Plans and executes multi-channel campaigns",
                    "Manages marketing budgets effectively",
                    "Analyzes campaign performance and ROI",
                    "Develops content strategies",
                    "Generates and nurtures leads",
                    "Uses marketing automation tools"
                ],
                weight=1.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.ANALYSIS,
                description="Develops marketing strategy and optimizes marketing mix.",
                keywords=["marketing strategy", "market research", "customer segmentation", "positioning"],
                criteria=[
                    "Develops comprehensive marketing strategies",
                    "Conducts market research and analysis",
                    "Performs customer segmentation and targeting",
                    "Defines brand positioning and messaging",
                    "Optimizes marketing mix and channels",
                    "Analyzes competitive landscape"
                ],
                weight=1.2
            ),
            RubricDescriptor(
                level=CompetencyLevel.SYNTHESIS,
                description="Creates innovative marketing programs and builds brand identity.",
                keywords=["brand building", "growth marketing", "innovation", "omnichannel"],
                criteria=[
                    "Builds and scales brand identity",
                    "Creates innovative growth marketing programs",
                    "Designs omnichannel customer experiences",
                    "Launches products successfully",
                    "Integrates marketing across organization",
                    "Drives significant customer acquisition"
                ],
                weight=1.5
            ),
            RubricDescriptor(
                level=CompetencyLevel.MASTERY,
                description="Marketing expert with proven track record of business growth.",
                keywords=["marketing leadership", "revenue impact", "brand success", "team building"],
                criteria=[
                    "Proven track record of revenue growth",
                    "Builds successful brands from scratch",
                    "Manages large marketing teams",
                    "Expert in multiple marketing channels",
                    "Significant business impact through marketing",
                    "Recognized marketing expert"
                ],
                weight=2.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.INFLUENCE,
                description="Marketing visionary shaping brand and market direction.",
                keywords=["CMO-level", "market leadership", "brand vision", "industry influence"],
                criteria=[
                    "Sets marketing vision for organization",
                    "Influences industry marketing practices",
                    "Speaks at major marketing conferences",
                    "Drives company-wide growth",
                    "Builds and leads marketing organizations",
                    "Strong external marketing reputation"
                ],
                weight=2.5
            )
        ]

        return Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Marketing Manager",
            skill_name="Marketing & Brand Management",
            descriptors=descriptors
        )

    @staticmethod
    def sales_representative() -> Rubric:
        """Rubric for Sales Representative positions"""
        descriptors = [
            RubricDescriptor(
                level=CompetencyLevel.AWARENESS,
                description="Understands sales process and can conduct basic sales activities.",
                keywords=["prospecting", "cold calling", "CRM", "product knowledge", "qualification"],
                criteria=[
                    "Prospects and qualifies leads",
                    "Conducts product demos",
                    "Uses CRM systems effectively",
                    "Understands sales methodology basics",
                    "Handles basic objections"
                ],
                weight=0.8
            ),
            RubricDescriptor(
                level=CompetencyLevel.APPLICATION,
                description="Consistently meets sales targets and manages sales pipeline.",
                keywords=["quota attainment", "pipeline management", "negotiation", "closing"],
                criteria=[
                    "Consistently meets or exceeds quota",
                    "Manages sales pipeline effectively",
                    "Negotiates deals successfully",
                    "Closes deals independently",
                    "Builds strong customer relationships",
                    "Forecasts accurately"
                ],
                weight=1.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.ANALYSIS,
                description="Develops sales strategy and manages complex deal cycles.",
                keywords=["enterprise sales", "strategic selling", "account planning", "complex deals"],
                criteria=[
                    "Manages complex enterprise sales cycles",
                    "Develops account strategies and plans",
                    "Navigates organizational buying processes",
                    "Identifies upsell and cross-sell opportunities",
                    "Analyzes customer needs deeply",
                    "Coaches junior sales reps"
                ],
                weight=1.2
            ),
            RubricDescriptor(
                level=CompetencyLevel.SYNTHESIS,
                description="Builds sales programs and opens new markets.",
                keywords=["new market", "sales playbook", "partnership", "territory building"],
                criteria=[
                    "Opens and builds new markets or territories",
                    "Creates sales playbooks and methodologies",
                    "Develops strategic partnerships",
                    "Designs sales programs and incentives",
                    "Significantly exceeds targets consistently",
                    "Establishes sales best practices"
                ],
                weight=1.5
            ),
            RubricDescriptor(
                level=CompetencyLevel.MASTERY,
                description="Sales expert with exceptional track record and revenue impact.",
                keywords=["top performer", "sales leadership", "revenue growth", "deal maker"],
                criteria=[
                    "Consistently top sales performer",
                    "Closes transformational deals",
                    "Mentors and develops sales teams",
                    "Drives significant revenue growth",
                    "Expert in multiple sales methodologies",
                    "Recognized sales authority"
                ],
                weight=2.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.INFLUENCE,
                description="Sales leader shaping sales organization and go-to-market strategy.",
                keywords=["sales leadership", "GTM strategy", "revenue transformation", "CRO-level"],
                criteria=[
                    "Defines go-to-market strategy",
                    "Builds and scales sales organizations",
                    "Influences industry sales practices",
                    "Drives company revenue transformation",
                    "Speaks at sales conferences",
                    "Strong reputation in sales community"
                ],
                weight=2.5
            )
        ]

        return Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Sales Representative",
            skill_name="Sales & Business Development",
            descriptors=descriptors
        )

    @staticmethod
    def hr_manager() -> Rubric:
        """Rubric for HR Manager positions"""
        descriptors = [
            RubricDescriptor(
                level=CompetencyLevel.AWARENESS,
                description="Understands HR processes and handles routine HR tasks.",
                keywords=["recruiting", "onboarding", "HR systems", "policies", "employee relations"],
                criteria=[
                    "Manages recruitment processes",
                    "Conducts employee onboarding",
                    "Uses HR information systems",
                    "Understands employment law basics",
                    "Handles routine employee relations"
                ],
                weight=0.8
            ),
            RubricDescriptor(
                level=CompetencyLevel.APPLICATION,
                description="Manages HR programs and provides strategic HR support.",
                keywords=["talent management", "performance management", "compensation", "training"],
                criteria=[
                    "Implements talent management programs",
                    "Manages performance review processes",
                    "Develops compensation and benefits strategies",
                    "Creates training and development programs",
                    "Resolves complex employee relations issues",
                    "Partners with business leaders"
                ],
                weight=1.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.ANALYSIS,
                description="Develops HR strategy and drives organizational effectiveness.",
                keywords=["HR strategy", "org design", "workforce planning", "culture"],
                criteria=[
                    "Develops HR strategies aligned with business",
                    "Designs organizational structures",
                    "Conducts workforce planning and analytics",
                    "Shapes organizational culture",
                    "Manages organizational change initiatives",
                    "Uses data for HR decision-making"
                ],
                weight=1.2
            ),
            RubricDescriptor(
                level=CompetencyLevel.SYNTHESIS,
                description="Transforms HR function and builds comprehensive people programs.",
                keywords=["HR transformation", "employer branding", "talent strategy", "innovation"],
                criteria=[
                    "Transforms HR functions and processes",
                    "Builds employer brand and EVP",
                    "Creates comprehensive talent strategies",
                    "Innovates HR programs and policies",
                    "Integrates HR across organization",
                    "Drives significant cultural change"
                ],
                weight=1.5
            ),
            RubricDescriptor(
                level=CompetencyLevel.MASTERY,
                description="HR expert recognized for excellence in people management.",
                keywords=["HR excellence", "best practices", "HR leadership", "certifications"],
                criteria=[
                    "Recognized HR expert in specialization",
                    "Sets HR best practices and standards",
                    "Holds advanced HR certifications (SPHR, SHRM-SCP)",
                    "Drives measurable business impact through HR",
                    "Builds high-performing HR teams",
                    "Mentors senior HR professionals"
                ],
                weight=2.0
            ),
            RubricDescriptor(
                level=CompetencyLevel.INFLUENCE,
                description="HR leader shaping people strategy and organizational success.",
                keywords=["CHRO-level", "people strategy", "board-level", "transformation"],
                criteria=[
                    "Defines organizational people strategy",
                    "Board-level or C-suite HR leadership",
                    "Influences industry HR practices",
                    "Speaks at major HR conferences",
                    "Drives company-wide transformation",
                    "Strong external HR reputation"
                ],
                weight=2.5
            )
        ]

        return Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="HR Manager",
            skill_name="Human Resources Management",
            descriptors=descriptors
        )

    @staticmethod
    def get_all_rubrics() -> List[Rubric]:
        """Get all professional rubrics"""
        return [
            ProfessionalRubrics.software_engineer(),
            ProfessionalRubrics.data_scientist(),
            ProfessionalRubrics.product_manager(),
            ProfessionalRubrics.devops_engineer(),
            ProfessionalRubrics.ux_designer(),
            ProfessionalRubrics.security_engineer(),
            ProfessionalRubrics.business_analyst(),
            ProfessionalRubrics.marketing_manager(),
            ProfessionalRubrics.sales_representative(),
            ProfessionalRubrics.hr_manager()
        ]

    @staticmethod
    def get_rubric_by_role(role_name: str) -> Rubric:
        """Get rubric by role name"""
        rubrics_map = {
            "Software Engineer": ProfessionalRubrics.software_engineer,
            "Data Scientist": ProfessionalRubrics.data_scientist,
            "Product Manager": ProfessionalRubrics.product_manager,
            "DevOps Engineer": ProfessionalRubrics.devops_engineer,
            "UX Designer": ProfessionalRubrics.ux_designer,
            "Security Engineer": ProfessionalRubrics.security_engineer,
            "Business Analyst": ProfessionalRubrics.business_analyst,
            "Marketing Manager": ProfessionalRubrics.marketing_manager,
            "Sales Representative": ProfessionalRubrics.sales_representative,
            "HR Manager": ProfessionalRubrics.hr_manager
        }

        rubric_func = rubrics_map.get(role_name)
        if rubric_func:
            return rubric_func()
        else:
            raise ValueError(f"Rubric not found for role: {role_name}")
