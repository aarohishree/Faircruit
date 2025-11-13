import pandas as pd
import os
from typing import Dict, List

class RubricsReader:
    def __init__(self, folder_path="."):
        self.folder_path = folder_path
        self.rubrics_data = {}

    def load_all_rubrics(self):
        """Load all Excel files and extract rubrics for each job role"""
        excel_files = [f for f in os.listdir(self.folder_path) if f.endswith('.xlsx') and 'competency' in f.lower()]

        for excel_file in excel_files:
            file_path = os.path.join(self.folder_path, excel_file)
            try:
                xl_file = pd.ExcelFile(file_path)

                for sheet_name in xl_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)

                    # Clean job role name
                    job_role = sheet_name.strip()

                    # Parse competencies and rubrics
                    competencies = self._parse_competencies(df)

                    if competencies:
                        self.rubrics_data[job_role] = {
                            'competencies': competencies,
                            'source_file': excel_file
                        }
            except Exception as e:
                print(f"Error reading {excel_file}: {e}")

        return self.rubrics_data

    def _parse_competencies(self, df: pd.DataFrame) -> List[Dict]:
        """Parse competencies from DataFrame"""
        competencies = []
        current_competency = None

        for _, row in df.iterrows():
            competency_name = row.get('Competencies')
            level = row.get('Levels')
            rubric = row.get('Rubrics')

            # Check if this is a new competency
            if pd.notna(competency_name) and str(competency_name).strip():
                current_competency = {
                    'name': str(competency_name).strip(),
                    'levels': {}
                }
                competencies.append(current_competency)

            # Add level and rubric to current competency
            if current_competency and pd.notna(level) and pd.notna(rubric):
                level_str = str(level).strip()
                rubric_str = str(rubric).strip()
                current_competency['levels'][level_str] = rubric_str

        return competencies

    def get_job_roles(self) -> List[str]:
        """Get list of available job roles"""
        return list(self.rubrics_data.keys())

    def get_rubrics_for_role(self, job_role: str) -> Dict:
        """Get rubrics for a specific job role"""
        return self.rubrics_data.get(job_role, {})

    def format_rubrics_for_gemini(self, job_role: str) -> str:
        """Format rubrics as a string for Gemini prompt"""
        rubrics = self.get_rubrics_for_role(job_role)
        if not rubrics:
            return ""

        formatted = f"Job Role: {job_role}\n\n"
        formatted += "Competencies and Evaluation Criteria:\n"
        formatted += "=" * 80 + "\n\n"

        for comp in rubrics.get('competencies', []):
            formatted += f"Competency: {comp['name']}\n"
            formatted += "-" * 80 + "\n"

            for level, criteria in comp['levels'].items():
                formatted += f"\n{level} Level:\n{criteria}\n"

            formatted += "\n" + "=" * 80 + "\n\n"

        return formatted
