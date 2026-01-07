"""
InterviewAgent - Generates interview questions and preparation tips.
Uses Google ADK for intelligent interview question generation.
"""

from google import generativeai as genai
import json
import os


class InterviewAgent:
    def __init__(self, api_key: str = None):
        """Initialize InterviewAgent with Google ADK."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        # Using gemini-2.0-flash for better performance and speed
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def generate_questions(self, target_role: str, technical_skills: list, 
                          experience_summary: str, num_technical: int = 10, 
                          num_behavioral: int = 8) -> dict:
        """
        Generate interview questions for the target role.
        
        Args:
            target_role: Target job role
            technical_skills: List of relevant technical skills
            experience_summary: User's experience summary
            num_technical: Number of technical questions to generate
            num_behavioral: Number of behavioral questions to generate
            
        Returns:
            Dictionary with questions and preparation tips
        """
        prompt = f"""Generate interview questions to prepare for the target job role.

Target Role: {target_role}
Relevant Skills: {', '.join(technical_skills)}
Candidate Experience: {experience_summary}

Generate {num_technical} technical questions and {num_behavioral} behavioral questions.

Return a JSON response with the following structure:
{{
    "target_role": "{target_role}",
    "technical_questions": [
        {{
            "question": "Question text",
            "category": "category (e.g., Programming, System Design, Algorithms)",
            "difficulty": "Easy|Medium|Hard",
            "tips": "Brief tip on how to approach this question"
        }}
    ],
    "behavioral_questions": [
        {{
            "question": "Question text",
            "focus_area": "focus area (e.g., Leadership, Problem-solving, Teamwork)",
            "tips": "What interviewers are looking for in the answer"
        }}
    ],
    "preparation_tips": [
        "tip1",
        "tip2",
        "tip3"
    ],
    "common_red_flags": ["red flag 1", "red flag 2"],
    "success_strategies": ["strategy1", "strategy2", "strategy3"]
}}

Instructions:
- Generate {num_technical} technical questions relevant to the role and skills
- Generate {num_behavioral} behavioral questions (STAR method applicable)
- Include difficulty levels for technical questions
- Provide tips for answering each question
- Add general preparation tips (5-7 tips)
- List common mistakes/red flags to avoid
- Include success strategies for interviews

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
            result.setdefault("target_role", target_role)
            result.setdefault("technical_questions", [])
            result.setdefault("behavioral_questions", [])
            result.setdefault("preparation_tips", [])
            result.setdefault("common_red_flags", [])
            result.setdefault("success_strategies", [])
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                "target_role": target_role,
                "technical_questions": [],
                "behavioral_questions": [],
                "preparation_tips": ["Review your technical skills", "Practice the STAR method"],
                "common_red_flags": [],
                "success_strategies": [],
                "error": str(e)
            }
        except Exception as e:
            return {
                "target_role": target_role,
                "technical_questions": [],
                "behavioral_questions": [],
                "preparation_tips": ["Review your technical skills", "Practice the STAR method"],
                "common_red_flags": [],
                "success_strategies": [],
                "error": str(e)
            }

