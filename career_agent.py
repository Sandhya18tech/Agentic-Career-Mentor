"""
CareerAgent - Recommends best-fit job roles based on user's skills and experience.
Uses Google ADK for intelligent career path recommendations.
"""

from google import generativeai as genai
import json
import os


class CareerAgent:
    def __init__(self, api_key: str = None):
        """Initialize CareerAgent with Google ADK."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        # Using gemini-2.0-flash for better performance and speed
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def recommend_careers(self, technical_skills: list, soft_skills: list, 
                         experience_summary: str, years_of_experience: int = 0) -> dict:
        """
        Recommend career paths based on user's profile.
        
        Args:
            technical_skills: List of technical skills
            soft_skills: List of soft skills
            experience_summary: Summary of experience
            years_of_experience: Years of professional experience
            
        Returns:
            Dictionary with recommended roles and alternatives
        """
        prompt = f"""Based on the user's profile, recommend the best-fit job role and alternative roles.

Technical Skills: {', '.join(technical_skills)}
Soft Skills: {', '.join(soft_skills)}
Experience: {experience_summary}
Years of Experience: {years_of_experience}

Return a JSON response with the following structure:
{{
    "best_fit_role": {{
        "title": "Job Title",
        "match_score": 9.0,
        "reasoning": "Why this role is the best fit (2-3 sentences)"
    }},
    "alternative_roles": [
        {{
            "title": "Alternative Job Title 1",
            "match_score": 8.0,
            "reasoning": "Why this is a good alternative (1-2 sentences)"
        }},
        {{
            "title": "Alternative Job Title 2",
            "match_score": 7.5,
            "reasoning": "Why this is a good alternative (1-2 sentences)"
        }}
    ],
    "career_insights": "Additional insights about career progression and opportunities (2-3 sentences)"
}}

Instructions:
- Recommend 1 best-fit role based on skills and experience
- Suggest 1-2 alternative roles that are viable options
- Provide match scores (0-10) for each role
- Give clear reasoning for each recommendation
- Include career insights

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
            result.setdefault("best_fit_role", {
                "title": "Not specified",
                "match_score": 0.0,
                "reasoning": "Unable to determine"
            })
            result.setdefault("alternative_roles", [])
            result.setdefault("career_insights", "No additional insights available")
            
            # Ensure we have 1-2 alternative roles
            if len(result["alternative_roles"]) > 2:
                result["alternative_roles"] = result["alternative_roles"][:2]
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                "best_fit_role": {
                    "title": "Error",
                    "match_score": 0.0,
                    "reasoning": "Error analyzing career options"
                },
                "alternative_roles": [],
                "career_insights": "Unable to generate recommendations",
                "error": str(e)
            }
        except Exception as e:
            return {
                "best_fit_role": {
                    "title": "Error",
                    "match_score": 0.0,
                    "reasoning": f"Error: {str(e)}"
                },
                "alternative_roles": [],
                "career_insights": "Unable to generate recommendations",
                "error": str(e)
            }

