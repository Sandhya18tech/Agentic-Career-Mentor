"""
RoadmapAgent - Creates structured learning roadmaps for skill development.
Uses Google ADK for personalized learning path generation.
"""

from google import generativeai as genai
import json
import os


class RoadmapAgent:
    def __init__(self, api_key: str = None):
        """Initialize RoadmapAgent with Google ADK."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        # Using gemini-2.0-flash for better performance and speed
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def create_roadmap(self, target_role: str, missing_skills: list, 
                      current_skills: list, months: int = 6) -> dict:
        """
        Create a structured learning roadmap.
        
        Args:
            target_role: Target job role
            missing_skills: List of skills to learn (can include priority info)
            current_skills: User's current skills
            months: Duration of roadmap (3-6 months)
            
        Returns:
            Dictionary with structured roadmap
        """
        # Prepare skills list with priorities if available
        skills_text = ""
        if isinstance(missing_skills, list) and len(missing_skills) > 0:
            if isinstance(missing_skills[0], dict):
                skills_text = ", ".join([f"{s.get('skill', '')} ({s.get('priority', 'Medium')})" 
                                        for s in missing_skills])
            else:
                skills_text = ", ".join(missing_skills)
        else:
            skills_text = "No specific skills provided"
        
        prompt = f"""Create a structured {months}-month learning roadmap to prepare for the target job role.

Target Role: {target_role}
Skills to Learn: {skills_text}
Current Skills: {', '.join(current_skills)}

Return a JSON response with the following structure:
{{
    "roadmap_duration": {months},
    "target_role": "{target_role}",
    "monthly_goals": [
        {{
            "month": 1,
            "focus_areas": ["area1", "area2", "area3"],
            "learning_objectives": ["objective1", "objective2"],
            "skills_to_acquire": ["skill1", "skill2"],
            "practice_projects": ["project1", "project2"],
            "resources": ["resource1", "resource2"]
        }},
        ...
    ],
    "overall_strategy": "High-level learning strategy for the entire roadmap (2-3 sentences)",
    "success_metrics": ["metric1", "metric2", "metric3"]
}}

Instructions:
- Break down the roadmap into monthly goals (for {months} months)
- Each month should have 2-4 focus areas
- Include specific learning objectives for each month
- List skills to acquire each month
- Suggest 1-2 practice projects per month (real-world applicable)
- Recommend learning resources (courses, books, tutorials)
- Provide an overall learning strategy
- Include success metrics to track progress

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
            result.setdefault("roadmap_duration", months)
            result.setdefault("target_role", target_role)
            result.setdefault("monthly_goals", [])
            result.setdefault("overall_strategy", "No strategy provided")
            result.setdefault("success_metrics", [])
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                "roadmap_duration": months,
                "target_role": target_role,
                "monthly_goals": [],
                "overall_strategy": "Error creating roadmap",
                "success_metrics": [],
                "error": str(e)
            }
        except Exception as e:
            return {
                "roadmap_duration": months,
                "target_role": target_role,
                "monthly_goals": [],
                "overall_strategy": f"Error: {str(e)}",
                "success_metrics": [],
                "error": str(e)
            }

