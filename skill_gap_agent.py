"""
SkillGapAgent - Compares user skills with target job role and identifies gaps.
Uses Google ADK for intelligent skill gap analysis.
"""

from google import generativeai as genai
import json
import os


class SkillGapAgent:
    def __init__(self, api_key: str = None):
        """Initialize SkillGapAgent with Google ADK."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        # Using gemini-2.0-flash for better performance and speed
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def analyze_gaps(self, user_skills: list, target_role: str, experience_summary: str = "") -> dict:
        """
        Analyze skill gaps between user skills and target role requirements.
        
        Args:
            user_skills: List of user's technical and soft skills
            target_role: Target job role (e.g., "Senior Software Engineer", "Data Scientist")
            experience_summary: Optional summary of user's experience
            
        Returns:
            Dictionary with missing skills and priorities
        """
        prompt = f"""Analyze skill gaps between the user's skills and the requirements for the target job role.

User's Skills: {', '.join(user_skills)}
Target Job Role: {target_role}
User's Experience: {experience_summary}

Return a JSON response with the following structure:
{{
    "missing_skills": [
        {{
            "skill": "skill name",
            "priority": "High|Medium|Low",
            "reason": "Why this skill is important for the role"
        }}
    ],
    "gap_analysis": "Overall summary of skill gaps in 2-3 sentences",
    "readiness_score": 7.5
}}

Instructions:
- Identify missing skills required for the target role
- Prioritize gaps as High (critical for role), Medium (important), or Low (nice to have)
- Provide brief reasoning for each missing skill
- Calculate a readiness score (0-10) based on how well the user's skills match the role
- Write a brief gap analysis summary

Return ONLY valid JSON, no additional text."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response text
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            # Ensure required fields
            result.setdefault("missing_skills", [])
            result.setdefault("gap_analysis", "No gaps identified")
            result.setdefault("readiness_score", 0.0)
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                "missing_skills": [],
                "gap_analysis": "Error analyzing skill gaps",
                "readiness_score": 0.0,
                "error": str(e)
            }
        except Exception as e:
            return {
                "missing_skills": [],
                "gap_analysis": f"Error: {str(e)}",
                "readiness_score": 0.0,
                "error": str(e)
            }

