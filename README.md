An agentic AI app that analyzes a resume, identifies skill gaps, recommends career paths, generates a 3–6 month learning roadmap, and prepares interview questions. Built with FastAPI (backend), React (frontend), and Google Generative AI.

Model: gemini-2.0-flash-exp (fast, low-latency). You can switch to gemini-2.0-flash or gemini-1.5-pro if needed.

Features

- ResumeAgent: extract technical/soft skills, summarize experience, rate resume (0–10)
- SkillGapAgent: compare skills to a target role, identify/prioritize gaps (High/Medium/Low)
- CareerAgent: recommend best-fit role + 1–2 alternatives with reasoning
- RoadmapAgent: create structured 3–6 month roadmap with monthly goals, projects, resources
- InterviewAgent: generate technical and behavioral questions + prep tips
- RootAgent: orchestrates all agents sequentially and returns a unified JSON response

Tech Stack

- Backend: Python, FastAPI, Pydantic, Uvicorn
- AI: Google Generative AI (Gemini)
- Frontend: React (Create React App), Axios
- Orchestration: Sequential agent workflow

save you api key credential and other variables in .env
