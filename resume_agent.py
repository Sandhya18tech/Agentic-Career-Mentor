"""
ResumeAgent - Extracts skills, summarizes experience, and rates resume strength.
Uses Google ADK for AI-powered resume analysis.
"""

from google import generativeai as genai
import json
import os


class ResumeAgent:
    def __init__(self, api_key: str = None):
        """Initialize ResumeAgent with Google ADK."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        # Using gemini-2.0-flash for better performance and speed
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def analyze(self, resume_text: str) -> dict:
        """
        Analyze resume and extract:
        - Technical skills
        - Soft skills
        - Experience level summary
        - Resume strength rating (0-10)
        
        Args:
            resume_text: The resume content as text
            
        Returns:
            Dictionary with extracted information
        """
        prompt = f"""Analyze the following resume and extract key information. 
Return a JSON response with the following structure:
{{
    "technical_skills": ["skill1", "skill2", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "experience_summary": "Brief summary of experience level and years",
    "resume_strength": 7.5,
    "years_of_experience": 3
}}

Resume Text:
{resume_text}

Instructions:
- Extract all technical skills (programming languages, tools, frameworks, technologies)
- Extract soft skills (communication, leadership, teamwork, etc.)
- Summarize experience level in 2-3 sentences
- Rate resume strength from 0-10 based on clarity, completeness, relevant experience, and skills
- Estimate years of experience if mentioned

Return ONLY valid JSON, no additional text."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response text (remove markdown code blocks if present)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            # Ensure all required fields are present
            result.setdefault("technical_skills", [])
            result.setdefault("soft_skills", [])
            result.setdefault("experience_summary", "Not specified")
            result.setdefault("resume_strength", 0.0)
            result.setdefault("years_of_experience", 0)
            
            return result
            
        except json.JSONDecodeError as e:
            # Fallback parsing if JSON is malformed
            return {
                "technical_skills": [],
                "soft_skills": [],
                "experience_summary": "Error parsing resume",
                "resume_strength": 0.0,
                "years_of_experience": 0,
                "error": str(e)
            }
        except Exception as e:
            return {
                "technical_skills": [],
                "soft_skills": [],
                "experience_summary": f"Error analyzing resume: {str(e)}",
                "resume_strength": 0.0,
                "years_of_experience": 0,
                "error": str(e)
            }

