import React, { useState } from 'react';
import './App.css';
import axios from 'axios';

// Backend API URL - Update this if your backend runs on a different address/port
// Common options: 'http://localhost:8000' or 'http://127.0.0.1:8000'
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [resumeText, setResumeText] = useState('');
  const [targetRole, setTargetRole] = useState('');
  const [roadmapMonths, setRoadmapMonths] = useState(6);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('input');
  const [expandedSections, setExpandedSections] = useState({});

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleAnalyze = async () => {
    if (!resumeText.trim() || resumeText.length < 50) {
      setError('Please enter at least 50 characters of resume text.');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setActiveTab('results');

    try {
      // First check if backend is running
      try {
        await axios.get(`${API_BASE_URL}/health`);
      } catch (healthErr) {
        throw new Error(
          `Cannot connect to backend server at ${API_BASE_URL}. ` +
          `Make sure the FastAPI backend is running on port 8000. ` +
          `Error: ${healthErr.message}`
        );
      }

      const response = await axios.post(
        `${API_BASE_URL}/analyze`,
        {
          resume_text: resumeText,
          target_role: targetRole || null,
          roadmap_months: roadmapMonths
        },
        {
          timeout: 120000 // 2 minutes timeout for AI processing
        }
      );

      setResults(response.data);
      setExpandedSections({
        resume: true,
        career: true,
        gaps: false,
        roadmap: false,
        interview: false
      });
    } catch (err) {
      if (err.message && err.message.includes('Cannot connect')) {
        setError(err.message);
      } else if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
        setError(
          `❌ Connection failed! Make sure the backend server is running:\n` +
          `1. Open a terminal\n` +
          `2. Navigate to the backend folder: cd backend\n` +
          `3. Run: python main.py\n` +
          `4. Wait for "Career Mentor AI Agent initialized successfully!" message\n` +
          `5. Then try again`
        );
      } else if (err.response?.data?.detail) {
        setError(`Error: ${err.response.data.detail}`);
      } else if (err.message) {
        setError(`Error: ${err.message}`);
      } else {
        setError('An error occurred during analysis. Please check the backend server logs.');
      }
    } finally {
      setLoading(false);
    }
  };

  const renderSummary = () => {
    if (!results?.summary) return null;

    const s = results.summary;
    return (
      <div className="summary-card">
        <h2>📊 Analysis Summary</h2>
        <div className="summary-grid">
          <div className="summary-item">
            <span className="summary-label">Resume Strength:</span>
            <span className="summary-value">{s.resume_strength?.toFixed(1)}/10</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Recommended Role:</span>
            <span className="summary-value">{s.recommended_role}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Readiness Score:</span>
            <span className="summary-value">{s.readiness_score?.toFixed(1)}/10</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Skill Gaps:</span>
            <span className="summary-value">{s.total_skill_gaps}</span>
          </div>
        </div>
      </div>
    );
  };

  const renderResumeAnalysis = () => {
    if (!results?.data?.resume_analysis) return null;

    const ra = results.data.resume_analysis;
    return (
      <div className="section-card">
        <div className="section-header" onClick={() => toggleSection('resume')}>
          <h3>📄 Resume Analysis</h3>
          <span className="toggle-icon">{expandedSections.resume ? '−' : '+'}</span>
        </div>
        {expandedSections.resume && (
          <div className="section-content">
            <div className="info-row">
              <strong>Resume Strength:</strong>
              <span className="rating">{ra.resume_strength?.toFixed(1)}/10</span>
            </div>
            <div className="info-row">
              <strong>Experience Summary:</strong>
              <p>{ra.experience_summary}</p>
            </div>
            <div className="info-row">
              <strong>Years of Experience:</strong>
              <span>{ra.years_of_experience || 'Not specified'}</span>
            </div>
            <div className="skills-container">
              <div className="skills-section">
                <h4>Technical Skills:</h4>
                <div className="skills-list">
                  {ra.technical_skills?.map((skill, idx) => (
                    <span key={idx} className="skill-tag">{skill}</span>
                  ))}
                </div>
              </div>
              <div className="skills-section">
                <h4>Soft Skills:</h4>
                <div className="skills-list">
                  {ra.soft_skills?.map((skill, idx) => (
                    <span key={idx} className="skill-tag soft">{skill}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderCareerRecommendations = () => {
    if (!results?.data?.career_recommendations) return null;

    const cr = results.data.career_recommendations;
    return (
      <div className="section-card">
        <div className="section-header" onClick={() => toggleSection('career')}>
          <h3>🎯 Career Recommendations</h3>
          <span className="toggle-icon">{expandedSections.career ? '−' : '+'}</span>
        </div>
        {expandedSections.career && (
          <div className="section-content">
            <div className="recommendation-card best-fit">
              <h4>Best Fit Role: {cr.best_fit_role?.title}</h4>
              <div className="match-score">Match Score: {cr.best_fit_role?.match_score?.toFixed(1)}/10</div>
              <p>{cr.best_fit_role?.reasoning}</p>
            </div>
            <div className="alternatives">
              <h4>Alternative Roles:</h4>
              {cr.alternative_roles?.map((role, idx) => (
                <div key={idx} className="recommendation-card">
                  <h5>{role.title}</h5>
                  <div className="match-score">Match Score: {role.match_score?.toFixed(1)}/10</div>
                  <p>{role.reasoning}</p>
                </div>
              ))}
            </div>
            {cr.career_insights && (
              <div className="insights">
                <h4>💡 Career Insights</h4>
                <p>{cr.career_insights}</p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderSkillGaps = () => {
    if (!results?.data?.skill_gap_analysis) return null;

    const sga = results.data.skill_gap_analysis;
    const missingSkills = sga.missing_skills || [];

    const highPriority = missingSkills.filter(s => s.priority === 'High');
    const mediumPriority = missingSkills.filter(s => s.priority === 'Medium');
    const lowPriority = missingSkills.filter(s => s.priority === 'Low');

    return (
      <div className="section-card">
        <div className="section-header" onClick={() => toggleSection('gaps')}>
          <h3>🔍 Skill Gap Analysis</h3>
          <span className="toggle-icon">{expandedSections.gaps ? '−' : '+'}</span>
        </div>
        {expandedSections.gaps && (
          <div className="section-content">
            <div className="info-row">
              <strong>Readiness Score:</strong>
              <span className="rating">{sga.readiness_score?.toFixed(1)}/10</span>
            </div>
            {sga.gap_analysis && (
              <div className="gap-summary">
                <p>{sga.gap_analysis}</p>
              </div>
            )}
            
            {highPriority.length > 0 && (
              <div className="priority-section high">
                <h4>🔴 High Priority Gaps</h4>
                {highPriority.map((skill, idx) => (
                  <div key={idx} className="gap-item">
                    <strong>{skill.skill}</strong>
                    <p>{skill.reason}</p>
                  </div>
                ))}
              </div>
            )}

            {mediumPriority.length > 0 && (
              <div className="priority-section medium">
                <h4>🟡 Medium Priority Gaps</h4>
                {mediumPriority.map((skill, idx) => (
                  <div key={idx} className="gap-item">
                    <strong>{skill.skill}</strong>
                    <p>{skill.reason}</p>
                  </div>
                ))}
              </div>
            )}

            {lowPriority.length > 0 && (
              <div className="priority-section low">
                <h4>🟢 Low Priority Gaps</h4>
                {lowPriority.map((skill, idx) => (
                  <div key={idx} className="gap-item">
                    <strong>{skill.skill}</strong>
                    <p>{skill.reason}</p>
                  </div>
                ))}
              </div>
            )}

            {missingSkills.length === 0 && (
              <p className="no-gaps">✅ No significant skill gaps identified!</p>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderRoadmap = () => {
    if (!results?.data?.learning_roadmap) return null;

    const roadmap = results.data.learning_roadmap;
    const monthlyGoals = roadmap.monthly_goals || [];

    return (
      <div className="section-card">
        <div className="section-header" onClick={() => toggleSection('roadmap')}>
          <h3>🗺️ Learning Roadmap ({roadmap.roadmap_duration} months)</h3>
          <span className="toggle-icon">{expandedSections.roadmap ? '−' : '+'}</span>
        </div>
        {expandedSections.roadmap && (
          <div className="section-content">
            {roadmap.overall_strategy && (
              <div className="strategy">
                <h4>Overall Strategy</h4>
                <p>{roadmap.overall_strategy}</p>
              </div>
            )}

            {monthlyGoals.map((month, idx) => (
              <div key={idx} className="month-card">
                <h4>Month {month.month}</h4>
                {month.focus_areas && month.focus_areas.length > 0 && (
                  <div className="roadmap-section">
                    <strong>Focus Areas:</strong>
                    <ul>
                      {month.focus_areas.map((area, i) => (
                        <li key={i}>{area}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {month.learning_objectives && month.learning_objectives.length > 0 && (
                  <div className="roadmap-section">
                    <strong>Learning Objectives:</strong>
                    <ul>
                      {month.learning_objectives.map((obj, i) => (
                        <li key={i}>{obj}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {month.skills_to_acquire && month.skills_to_acquire.length > 0 && (
                  <div className="roadmap-section">
                    <strong>Skills to Acquire:</strong>
                    <div className="skills-list">
                      {month.skills_to_acquire.map((skill, i) => (
                        <span key={i} className="skill-tag">{skill}</span>
                      ))}
                    </div>
                  </div>
                )}
                {month.practice_projects && month.practice_projects.length > 0 && (
                  <div className="roadmap-section">
                    <strong>Practice Projects:</strong>
                    <ul>
                      {month.practice_projects.map((project, i) => (
                        <li key={i}>{project}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {month.resources && month.resources.length > 0 && (
                  <div className="roadmap-section">
                    <strong>Resources:</strong>
                    <ul>
                      {month.resources.map((resource, i) => (
                        <li key={i}>{resource}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}

            {roadmap.success_metrics && roadmap.success_metrics.length > 0 && (
              <div className="metrics">
                <h4>Success Metrics</h4>
                <ul>
                  {roadmap.success_metrics.map((metric, idx) => (
                    <li key={idx}>{metric}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderInterviewPrep = () => {
    if (!results?.data?.interview_preparation) return null;

    const interview = results.data.interview_preparation;
    const techQuestions = interview.technical_questions || [];
    const behavioralQuestions = interview.behavioral_questions || [];

    return (
      <div className="section-card">
        <div className="section-header" onClick={() => toggleSection('interview')}>
          <h3>💼 Interview Preparation</h3>
          <span className="toggle-icon">{expandedSections.interview ? '−' : '+'}</span>
        </div>
        {expandedSections.interview && (
          <div className="section-content">
            <div className="questions-section">
              <h4>Technical Questions ({techQuestions.length})</h4>
              {techQuestions.map((q, idx) => (
                <div key={idx} className="question-card">
                  <div className="question-header">
                    <strong>Q{idx + 1}: {q.question}</strong>
                    <span className={`difficulty ${q.difficulty?.toLowerCase()}`}>
                      {q.difficulty}
                    </span>
                  </div>
                  {q.category && <div className="category">Category: {q.category}</div>}
                  {q.tips && <div className="tips">💡 {q.tips}</div>}
                </div>
              ))}
            </div>

            <div className="questions-section">
              <h4>Behavioral Questions ({behavioralQuestions.length})</h4>
              {behavioralQuestions.map((q, idx) => (
                <div key={idx} className="question-card">
                  <div className="question-header">
                    <strong>Q{idx + 1}: {q.question}</strong>
                  </div>
                  {q.focus_area && <div className="category">Focus: {q.focus_area}</div>}
                  {q.tips && <div className="tips">💡 {q.tips}</div>}
                </div>
              ))}
            </div>

            {interview.preparation_tips && interview.preparation_tips.length > 0 && (
              <div className="tips-section">
                <h4>Preparation Tips</h4>
                <ul>
                  {interview.preparation_tips.map((tip, idx) => (
                    <li key={idx}>{tip}</li>
                  ))}
                </ul>
              </div>
            )}

            {interview.success_strategies && interview.success_strategies.length > 0 && (
              <div className="tips-section">
                <h4>Success Strategies</h4>
                <ul>
                  {interview.success_strategies.map((strategy, idx) => (
                    <li key={idx}>{strategy}</li>
                  ))}
                </ul>
              </div>
            )}

            {interview.common_red_flags && interview.common_red_flags.length > 0 && (
              <div className="tips-section warning">
                <h4>⚠️ Common Red Flags to Avoid</h4>
                <ul>
                  {interview.common_red_flags.map((flag, idx) => (
                    <li key={idx}>{flag}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🤖 Career Mentor AI</h1>
        <p>Your intelligent career advisor powered by AI agents</p>
      </header>

      <div className="tabs">
        <button 
          className={activeTab === 'input' ? 'active' : ''} 
          onClick={() => setActiveTab('input')}
        >
          📝 Input
        </button>
        {results && (
          <button 
            className={activeTab === 'results' ? 'active' : ''} 
            onClick={() => setActiveTab('results')}
          >
            📊 Results
          </button>
        )}
      </div>

      {activeTab === 'input' && (
        <div className="input-container">
          <div className="input-card">
            <h2>Resume Analysis</h2>
            <div className="form-group">
              <label htmlFor="resume">Resume Text *</label>
              <textarea
                id="resume"
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your resume text here (minimum 50 characters)..."
                rows={10}
              />
              <small>{resumeText.length} characters</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="role">Target Role (Optional)</label>
                <input
                  id="role"
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="e.g., Senior Software Engineer"
                />
              </div>

              <div className="form-group">
                <label htmlFor="months">Roadmap Duration</label>
                <select
                  id="months"
                  value={roadmapMonths}
                  onChange={(e) => setRoadmapMonths(parseInt(e.target.value))}
                >
                  <option value={3}>3 months</option>
                  <option value={4}>4 months</option>
                  <option value={5}>5 months</option>
                  <option value={6}>6 months</option>
                </select>
              </div>
            </div>

            <button 
              className="analyze-button" 
              onClick={handleAnalyze}
              disabled={loading || resumeText.length < 50}
            >
              {loading ? 'Analyzing...' : '🚀 Analyze Resume'}
            </button>

            {error && (
              <div className="error-message">
                ⚠️ {error}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'results' && results && (
        <div className="results-container">
          {loading ? (
            <div className="loading">⏳ Analyzing your resume... Please wait.</div>
          ) : (
            <>
              {renderSummary()}
              {renderResumeAnalysis()}
              {renderCareerRecommendations()}
              {renderSkillGaps()}
              {renderRoadmap()}
              {renderInterviewPrep()}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;

