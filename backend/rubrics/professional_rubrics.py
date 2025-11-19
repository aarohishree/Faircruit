# professional_rubrics.py
import uuid
from typing import List
from models.schemas import CompetencyLevel, RubricDescriptor, Rubric


class ProfessionalRubrics:
    """Production-grade 4×4 competency rubrics for key technical roles."""

    # ===================================================================
    # 1. SOFTWARE ENGINEER – 4×4 Matrix
    # ===================================================================
    @staticmethod
    def software_engineer() -> List[Rubric]:
        rubrics = []

        # 1. Technical Excellence
        rubrics.append(Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Software Engineer",
            skill_name="Technical Excellence",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Writes clean, working code with guidance.",
                                 criteria=["Writes syntactically correct code", "Uses basic data structures", "Follows style guides", "Fixes simple bugs with help"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Delivers high-quality production code independently.",
                                 criteria=["Implements complex features", "Writes comprehensive tests", "Refactors effectively", "Optimizes performance"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes code quality and optimizes for trade-offs.",
                                 criteria=["Identifies performance bottlenecks", "Evaluates architectural trade-offs", "Analyzes code patterns", "Improves code readability"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes complex systems and establishes coding standards.",
                                 criteria=["Designs multi-component systems", "Establishes code quality standards", "Integrates best practices org-wide", "Leads architectural evolution"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Sets coding standards and solves deepest technical problems.",
                                 criteria=["Writes exemplary idiomatic code", "Introduces advanced patterns", "Drives code quality initiatives", "Resolves critical bugs"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Recognized coding authority internally and externally.",
                                 criteria=["Contributes to languages/runtimes", "Authors widely used libraries", "Code studied as reference", "Keynotes on paradigms"], weight=2.0),
            ]
        ))

        # 2. System Design & Architecture
        rubrics.append(Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Software Engineer",
            skill_name="System Design & Architecture",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Understands basic architecture concepts.",
                                 criteria=["Knows monolithic vs modular", "Reads architecture diagrams", "Understands REST/gRPC", "Follows existing patterns"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Designs robust, maintainable systems.",
                                 criteria=["Designs bounded services", "Chooses right databases/caches", "Handles scalability", "Writes design docs"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes trade-offs and optimizes system design.",
                                 criteria=["Evaluates architectural options", "Identifies bottlenecks", "Compares approaches", "Optimizes reliability"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes complex distributed systems.",
                                 criteria=["Designs multi-region systems", "Integrates patterns", "Handles recovery", "Builds resilience"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Architects large-scale distributed systems.",
                                 criteria=["Designs fault-tolerant systems", "Ensures observability/security", "Makes org-level trade-offs", "Creates frameworks"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Influences system design practices industry-wide.",
                                 criteria=["Designs systems at massive scale", "Publishes influential content", "Consulted by other companies", "Drives new paradigms"], weight=2.0),
            ]
        ))

        # 3. Professionalism & Collaboration
        rubrics.append(Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Software Engineer",
            skill_name="Professionalism & Collaboration",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Works well in a team with guidance.",
                                 criteria=["Communicates clearly", "Follows processes", "Accepts feedback", "Meets deadlines"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Proactive and collaborative team member.",
                                 criteria=["Runs effective meetings", "Gives/receives great reviews", "Mentors informally", "Improves processes"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes team dynamics and collaboration patterns.",
                                 criteria=["Identifies communication gaps", "Evaluates team effectiveness", "Analyzes conflict patterns", "Improves workflows"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes diverse perspectives into team strategy.",
                                 criteria=["Integrates multiple viewpoints", "Builds consensus", "Drives cross-team alignment", "Shapes team culture"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Role model for engineering culture.",
                                 criteria=["Fosters psychological safety", "Resolves conflicts", "Champions best practices org-wide", "Builds high-performing teams"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Shapes engineering culture beyond the company.",
                                 criteria=["Speaks/writes on culture", "Advises other companies", "Industry voice on excellence", "Influences open-source culture"], weight=2.0),
            ]
        ))

        # 4. Engineering Leadership & Influence
        rubrics.append(Rubric(
            rubric_id=str(uuid.uuid4()),
            role_name="Software Engineer",
            skill_name="Engineering Leadership & Influence",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Shows interest in leadership and impact.",
                                 criteria=["Volunteers for initiatives", "Helps teammates", "Participates in hiring", "Shares knowledge"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Tech leads projects and mentors others.",
                                 criteria=["Leads medium-large projects", "Defines team roadmaps", "Mentors engineers", "Represents team externally"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes leadership effectiveness and impact.",
                                 criteria=["Evaluates team performance", "Identifies growth opportunities", "Analyzes patterns", "Measures impact"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes leadership vision across teams.",
                                 criteria=["Aligns multiple teams", "Builds leadership culture", "Integrates diverse ideas", "Creates initiatives"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Drives org-wide technical strategy.",
                                 criteria=["Leads multi-team initiatives", "Sets technical vision", "Key in hiring/promotions", "Trusted by execs"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Global thought leader in software engineering.",
                                 criteria=["Keynotes at top conferences", "Authors books/papers", "Advises FAANG/startups", "Shapes the profession"], weight=2.0),
            ]
        ))

        return rubrics

    # ===================================================================
    # 2. AI/ML ENGINEER – 4×4 Matrix
    # ===================================================================
    @staticmethod
    def ai_ml_engineer() -> List[Rubric]:
        rubrics = []

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="AI/ML Engineer", skill_name="Model Development & Research",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Trains and evaluates basic models.", criteria=["Uses PyTorch/TensorFlow", "Proper train/val/test", "Basic tracking"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Builds and tunes production-grade models.", criteria=["Advanced feature engineering", "Hyperparameter optimization", "Reproduces SOTA"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes model performance and trade-offs.", criteria=["Evaluates architectures", "Compares approaches", "Analyzes failure modes", "Optimizes for metrics"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes novel model architectures.", criteria=["Combines techniques", "Designs new approaches", "Integrates multiple losses", "Builds frameworks"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Invents novel architectures or techniques.", criteria=["Publishes at top conferences", "Breaks benchmarks", "New training regimes"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Shapes future of AI research.", criteria=["Highly cited papers", "Core contributor to frameworks", "NeurIPS/ICML keynotes"], weight=2.0),
            ]))

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="AI/ML Engineer", skill_name="MLOps & Production Engineering",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Understands model deployment basics.", criteria=["Deploys via FastAPI", "Uses Docker", "Basic experiment tracking"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Productionizes models at scale.", criteria=["End-to-end MLOps", "Monitoring & drift", "Inference optimization"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes deployment and production challenges.", criteria=["Evaluates trade-offs", "Identifies bottlenecks", "Analyzes latency", "Optimizes infrastructure"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes end-to-end ML systems.", criteria=["Integrates pipelines", "Designs platforms", "Combines monitoring", "Builds automation"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Architects enterprise AI infrastructure.", criteria=["Distributed training", "LLM ops at scale", "Custom infra"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Defines global MLOps standards.", criteria=["Creator of Kubeflow/TFX", "MLOps World speaker", "FAANG consultant"], weight=2.0),
            ]))

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="AI/ML Engineer", skill_name="Data & Feature Platform",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Preprocesses data and builds features.", criteria=["Cleans datasets", "Simple transformations"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Builds scalable feature pipelines.", criteria=["Real-time & batch features", "Training/serving consistency", "Feature store"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes feature effectiveness and data quality.", criteria=["Evaluates feature importance", "Identifies data issues", "Analyzes distributions", "Optimizes pipelines"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes company-wide data platforms.", criteria=["Integrates sources", "Designs governance", "Combines architectures", "Builds frameworks"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Designs company-wide feature platform.", criteria=["Multi-modal platforms", "Data quality at scale", "Feature reuse"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Industry leader in feature systems.", criteria=["Creator of Feast/Tecton", "Publishes patterns", "Advises startups"], weight=2.0),
            ]))

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="AI/ML Engineer", skill_name="AI Leadership & Influence",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Shows interest in AI direction.", criteria=["Presents results", "Helps teammates"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Tech leads AI projects.", criteria=["Defines roadmaps", "Mentors juniors", "Cross-functional rep"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes AI strategy and impact.", criteria=["Evaluates initiatives", "Identifies opportunities", "Analyzes trends", "Measures effectiveness"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes AI vision across organization.", criteria=["Integrates teams", "Builds culture", "Combines expertise", "Creates strategy"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Drives org-wide AI strategy.", criteria=["Sets research agenda", "Builds world-class teams", "C-suite advisor"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Global AI thought leader.", criteria=["Major conference keynotes", "Advises on AI ethics/strategy", "Strong personal brand"], weight=2.0),
            ]))

        return rubrics

    # ===================================================================
    # 3. DATA ENGINEER – 4×4 Matrix
    # ===================================================================
    @staticmethod
    def data_engineer() -> List[Rubric]:
        rubrics = []

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="Data Engineer", skill_name="Data Pipeline Development",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Builds simple ETL jobs.", criteria=["Airflow/SQL scripts", "Basic data movement"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Builds reliable, monitored pipelines.", criteria=["Idempotent & testable", "Schema evolution", "CDC"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes pipeline performance and reliability.", criteria=["Identifies bottlenecks", "Evaluates approaches", "Analyzes data flow", "Optimizes throughput"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes complex data platforms.", criteria=["Integrates systems", "Designs patterns", "Combines architectures", "Builds frameworks"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Architects real-time, fault-tolerant platforms.", criteria=["Petabyte streaming", "Exactly-once", "Multi-region"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Creator of major data tools.", criteria=["Maintains dbt/Spark/Flink", "Data Council speaker"], weight=2.0),
            ]))

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="Data Engineer", skill_name="Data Architecture & Modeling",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Understands basic modeling.", criteria=["Star schema", "Simple models"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Designs performant models.", criteria=["Kimball/Data Vault", "Query optimization"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes data models and trade-offs.", criteria=["Evaluates schemas", "Identifies issues", "Compares approaches", "Optimizes queries"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes enterprise data architectures.", criteria=["Integrates patterns", "Designs governance", "Combines approaches", "Builds frameworks"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Defines enterprise data architecture.", criteria=["Data mesh/lakehouse", "Governance at scale"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Shapes modern data architecture.", criteria=["Author of data mesh concepts", "Advises Fortune 500"], weight=2.0),
            ]))

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="Data Engineer", skill_name="Data Platform & Infrastructure",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Uses cloud data services.", criteria=["BigQuery/Snowflake setup"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Manages cost-effective platforms.", criteria=["Cost optimization", "Partitioning/clustering"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.ANALYSIS, description="Analyzes infrastructure and optimization.", criteria=["Evaluates platforms", "Identifies bottlenecks", "Analyzes costs", "Optimizes usage"], weight=1.2),
                RubricDescriptor(level=CompetencyLevel.SYNTHESIS, description="Synthesizes enterprise data infrastructure.", criteria=["Integrates tools", "Designs architecture", "Combines platforms", "Builds solutions"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Builds internal data platforms.", criteria=["Runs Kafka/Spark at scale", "Self-service tools"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Industry voice on data infra.", criteria=["Open-source data tools", "Current/Strata keynote"], weight=2.0),
            ]))

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="Data Engineer", skill_name="Data Leadership & Strategy",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Owns data quality basics.", criteria=["Fixes pipelines", "Documents datasets"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Drives data reliability.", criteria=["Defines pipeline SLOs", "Mentors juniors"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Leads data organization.", criteria=["Heads Data Platform", "Aligns with business"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Recognized data engineering leader.", criteria=["Board advisor", "Author/speaker"], weight=2.0),
            ]))

        return rubrics

    # ===================================================================
    # 4. CYBERSECURITY ENGINEER – 4×4 Matrix
    # ===================================================================
    @staticmethod
    def cybersecurity_engineer() -> List[Rubric]:
        rubrics = []

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="Cybersecurity Engineer", skill_name="Threat Detection & Response",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Triages alerts using tools.", criteria=["SOC work", "Splunk/Sentinel"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Investigates and contains incidents.", criteria=["Root cause analysis", "Writes detection rules"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Leads red/blue/purple teams.", criteria=["Threat hunting programs", "APT simulation"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Global threat intelligence authority.", criteria=["Publishes TTP research", "Black Hat/DEF CON speaker"], weight=2.0),
            ]))

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="Cybersecurity Engineer", skill_name="Security Architecture & Engineering",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Implements basic controls.", criteria=["Firewall config", "OWASP"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Designs secure systems.", criteria=["Threat modeling", "Zero-trust"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Architects enterprise security platforms.", criteria=["Builds internal tools", "Drives compliance"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Shapes global security standards.", criteria=["Contributes to NIST", "Top bug bounty"], weight=2.0),
            ]))

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="Cybersecurity Engineer", skill_name="Incident Response & Forensics",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Assists in incident response.", criteria=["Log collection", "Follows playbooks"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Leads incident containment.", criteria=["Coordinates response", "Writes post-mortems"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="Runs enterprise IR program.", criteria=["Tabletop exercises", "Breach management"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="World-renowned IR expert.", criteria=["Author of IR frameworks", "Government advisor"], weight=2.0),
            ]))

        rubrics.append(Rubric(rubric_id=str(uuid.uuid4()), role_name="Cybersecurity Engineer", skill_name="Security Leadership & Culture",
            descriptors=[
                RubricDescriptor(level=CompetencyLevel.AWARENESS, description="Promotes basic hygiene.", criteria=["Phishing tests", "Reports vulns"], weight=0.8),
                RubricDescriptor(level=CompetencyLevel.APPLICATION, description="Drives security initiatives.", criteria=["Secure SDLC", "Developer training"], weight=1.0),
                RubricDescriptor(level=CompetencyLevel.MASTERY, description="CISO-level strategic leadership.", criteria=["Defines security strategy", "Board reporting"], weight=1.5),
                RubricDescriptor(level=CompetencyLevel.INFLUENCE, description="Global cybersecurity influencer.", criteria=["RSA keynote", "Nation-state policy advisor"], weight=2.0),
            ]))

        return rubrics