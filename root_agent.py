"""
Root Agent - Orchestrates all specialized agents in sequential order.
Passes context between agents and returns unified structured response.
"""

from .resume_agent import ResumeAgent
from .skill_gap_agent import SkillGapAgent
from .career_agent import CareerAgent
from .roadmap_agent import RoadmapAgent
from .interview_agent import InterviewAgent
import os


class RootAgent:
    """
    Root Agent that orchestrates the entire career mentoring workflow.
    
    Execution flow:
    1. ResumeAgent - Extract skills and experience from resume
    2. CareerAgent - Recommend best-fit role based on profile
    3. SkillGapAgent - Identify gaps for the recommended role
    4. RoadmapAgent - Create learning roadmap to fill gaps
    5. InterviewAgent - Generate interview questions for the role
    """
    
    def __init__(self, api_key: str = None):
        """Initialize RootAgent and all sub-agents."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Initialize all specialized agents
        self.resume_agent = ResumeAgent(self.api_key)
        self.skill_gap_agent = SkillGapAgent(self.api_key)
        self.career_agent = CareerAgent(self.api_key)
        self.roadmap_agent = RoadmapAgent(self.api_key)
        self.interview_agent = InterviewAgent(self.api_key)
    
    def analyze(self, resume_text: str, target_role: str = None, roadmap_months: int = 6) -> dict:
        """
        Execute the complete career mentoring workflow.
        
        Args:
            resume_text: The resume content as text
            target_role: Optional target role. If not provided, CareerAgent will recommend one.
            roadmap_months: Duration for learning roadmap (3-6 months)
            
        Returns:
            Unified structured response with all analysis results
        """
        context = {
            "resume_text": resume_text,
            "target_role": target_role,
            "roadmap_months": roadmap_months
        }
        
        results = {
            "resume_analysis": None,
            "career_recommendations": None,
            "skill_gap_analysis": None,
            "learning_roadmap": None,
            "interview_preparation": None,
            "errors": []
        }
        
        try:
            # Step 1: Analyze Resume
            print("Step 1: Analyzing resume...")
            resume_analysis = self.resume_agent.analyze(resume_text)
            results["resume_analysis"] = resume_analysis
            context.update({
                "technical_skills": resume_analysis.get("technical_skills", []),
                "soft_skills": resume_analysis.get("soft_skills", []),
                "experience_summary": resume_analysis.get("experience_summary", ""),
                "years_of_experience": resume_analysis.get("years_of_experience", 0)
            })
            
            # Step 2: Career Recommendations
            print("Step 2: Generating career recommendations...")
            career_recommendations = self.career_agent.recommend_careers(
                technical_skills=context["technical_skills"],
                soft_skills=context["soft_skills"],
                experience_summary=context["experience_summary"],
                years_of_experience=context["years_of_experience"]
            )
            results["career_recommendations"] = career_recommendations
            
            # Determine target role for subsequent steps
            if not target_role:
                target_role = career_recommendations.get("best_fit_role", {}).get("title", "Software Engineer")
            context["target_role"] = target_role
            
            # Step 3: Skill Gap Analysis
            print("Step 3: Analyzing skill gaps...")
            all_skills = context["technical_skills"] + context["soft_skills"]
            skill_gap_analysis = self.skill_gap_agent.analyze_gaps(
                user_skills=all_skills,
                target_role=target_role,
                experience_summary=context["experience_summary"]
            )
            results["skill_gap_analysis"] = skill_gap_analysis
            context["missing_skills"] = skill_gap_analysis.get("missing_skills", [])
            
            # Step 4: Learning Roadmap
            print("Step 4: Creating learning roadmap...")
            learning_roadmap = self.roadmap_agent.create_roadmap(
                target_role=target_role,
                missing_skills=context["missing_skills"],
                current_skills=all_skills,
                months=roadmap_months
            )
            results["learning_roadmap"] = learning_roadmap
            
            # Step 5: Interview Preparation
            print("Step 5: Generating interview questions...")
            interview_preparation = self.interview_agent.generate_questions(
                target_role=target_role,
                technical_skills=context["technical_skills"],
                experience_summary=context["experience_summary"]
            )
            results["interview_preparation"] = interview_preparation
            
            print("Analysis complete!")
            
        except Exception as e:
            error_msg = f"Error in workflow execution: {str(e)}"
            print(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    def get_summary(self, results: dict) -> dict:
        """
        Generate a high-level summary of the analysis results.
        
        Args:
            results: Results dictionary from analyze() method
            
        Returns:
            Summary dictionary
        """
        resume = results.get("resume_analysis", {})
        career = results.get("career_recommendations", {})
        gaps = results.get("skill_gap_analysis", {})
        roadmap = results.get("learning_roadmap", {})
        interview = results.get("interview_preparation", {})
        
        best_fit = career.get("best_fit_role", {})
        
        return {
            "resume_strength": resume.get("resume_strength", 0.0),
            "recommended_role": best_fit.get("title", "Not determined"),
            "readiness_score": gaps.get("readiness_score", 0.0),
            "total_skill_gaps": len(gaps.get("missing_skills", [])),
            "roadmap_duration": roadmap.get("roadmap_duration", 0),
            "interview_questions_generated": {
                "technical": len(interview.get("technical_questions", [])),
                "behavioral": len(interview.get("behavioral_questions", []))
            }
        }

