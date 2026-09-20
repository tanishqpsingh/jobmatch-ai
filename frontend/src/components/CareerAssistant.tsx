"use client";

import React, { useState } from "react";

type SubTool = "bullet" | "skill" | "questions" | "prep" | "tech" | "study";

export default function CareerAssistant() {
  const [activeSubTool, setActiveSubTool] = useState<SubTool>("bullet");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [resultData, setResultData] = useState<any>(null);

  // 1. Bullet Improver State
  const [bulletText, setBulletText] = useState<string>("Worked on python website backend and fixed database bugs.");
  const [bulletJobContext, setBulletJobContext] = useState<string>("Senior FastAPI Backend Engineer");

  // 2. Skill Explainer State
  const [skillName, setSkillName] = useState<string>("Kubernetes");
  const [skillJobContext, setSkillJobContext] = useState<string>("Cloud Native Backend Developer");

  // 3. Interview Questions State
  const [qJobTitle, setQJobTitle] = useState<string>("Senior Backend Engineer");
  const [qJobDesc, setQJobDesc] = useState<string>("Building high throughput FastAPI REST microservices with PostgreSQL and Docker.");

  // 4. Interview Prep Guide State
  const [prepJobTitle, setPrepJobTitle] = useState<string>("Backend Engineer (Python / FastAPI)");
  const [prepReqSkills, setPrepReqSkills] = useState<string>("Python, FastAPI, PostgreSQL, Docker");
  const [prepMissSkills, setPrepMissSkills] = useState<string>("Kubernetes, Redis");

  // 5. Tech Explainer State
  const [techName, setTechName] = useState<string>("Docker");
  const [techJobContext, setTechJobContext] = useState<string>("Backend Developer deploying microservices");

  // 6. Study Plan Generator State
  const [planMissingSkills, setPlanMissingSkills] = useState<string>("Docker, Kubernetes, Redis");
  const [planWeeks, setPlanWeeks] = useState<number>(4);

  const resetResult = () => {
    setResultData(null);
    setError(null);
  };

  const handleExecuteTool = async (endpoint: string, payload: any) => {
    setIsLoading(true);
    setError(null);
    setResultData(null);

    try {
      const res = await fetch(`http://localhost:8000/api/v1/career/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `API call failed with status ${res.status}`);
      }

      const data = await res.json();
      setResultData(data);
    } catch (err: any) {
      setError(err.message || "An error occurred while calling the AI Career Assistant.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-8">
      {/* Sub-tool Selector Bar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 backdrop-blur shadow-xl">
        <div className="flex flex-wrap justify-center gap-2">
          <button
            onClick={() => { setActiveSubTool("bullet"); resetResult(); }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
              activeSubTool === "bullet" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            ✏️ Bullet Improver
          </button>
          <button
            onClick={() => { setActiveSubTool("skill"); resetResult(); }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
              activeSubTool === "skill" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            💡 Missing Skill Explainer
          </button>
          <button
            onClick={() => { setActiveSubTool("questions"); resetResult(); }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
              activeSubTool === "questions" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            ❓ Interview Questions
          </button>
          <button
            onClick={() => { setActiveSubTool("prep"); resetResult(); }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
              activeSubTool === "prep" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            🎯 Interview Prep Guide
          </button>
          <button
            onClick={() => { setActiveSubTool("tech"); resetResult(); }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
              activeSubTool === "tech" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            ⚙️ Tech Explainer
          </button>
          <button
            onClick={() => { setActiveSubTool("study"); resetResult(); }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
              activeSubTool === "study" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            📅 Study Plan Generator
          </button>
        </div>
      </div>

      {/* Main Tool Form & Output Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur shadow-xl space-y-6">
        {/* Tool Header */}
        <div className="border-b border-slate-800 pb-4">
          <h2 className="text-xl font-bold text-white">
            {activeSubTool === "bullet" && "Resume Bullet Point Improver"}
            {activeSubTool === "skill" && "Missing Skill Explainer & Roadmap"}
            {activeSubTool === "questions" && "Tailored Interview Question Generator"}
            {activeSubTool === "prep" && "Job-Specific Interview Preparation Guide"}
            {activeSubTool === "tech" && "Technology Explainer for Job Roles"}
            {activeSubTool === "study" && "Structured Study Plan Generator"}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Gemini-powered career enhancement with strict factual integrity guarantees (no invented metrics or fake achievements).
          </p>
        </div>

        {/* 1. Bullet Improver Form */}
        {activeSubTool === "bullet" && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Original Bullet Point <span className="text-rose-400">*</span>
              </label>
              <textarea
                rows={3}
                value={bulletText}
                onChange={(e) => setBulletText(e.target.value)}
                placeholder="e.g. Worked on python website backend and fixed database bugs."
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Target Role / Context <span className="text-slate-500 lowercase">(optional)</span>
              </label>
              <input
                type="text"
                value={bulletJobContext}
                onChange={(e) => setBulletJobContext(e.target.value)}
                placeholder="e.g. Senior FastAPI Backend Engineer"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <button
              onClick={() => handleExecuteTool("improve-bullet", { bullet_text: bulletText, job_context: bulletJobContext || undefined })}
              disabled={isLoading || !bulletText.trim()}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition"
            >
              {isLoading ? "Improving Bullet..." : "Enhance Bullet Point"}
            </button>
          </div>
        )}

        {/* 2. Skill Explainer Form */}
        {activeSubTool === "skill" && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Missing Skill Name <span className="text-rose-400">*</span>
              </label>
              <input
                type="text"
                value={skillName}
                onChange={(e) => setSkillName(e.target.value)}
                placeholder="e.g. Kubernetes"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Job Context <span className="text-slate-500 lowercase">(optional)</span>
              </label>
              <input
                type="text"
                value={skillJobContext}
                onChange={(e) => setSkillJobContext(e.target.value)}
                placeholder="e.g. Cloud Native Backend Developer"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <button
              onClick={() => handleExecuteTool("explain-skill", { skill_name: skillName, job_context: skillJobContext || undefined })}
              disabled={isLoading || !skillName.trim()}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition"
            >
              {isLoading ? "Analyzing Skill..." : "Explain Missing Skill"}
            </button>
          </div>
        )}

        {/* 3. Interview Questions Form */}
        {activeSubTool === "questions" && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Target Job Title
              </label>
              <input
                type="text"
                value={qJobTitle}
                onChange={(e) => setQJobTitle(e.target.value)}
                placeholder="e.g. Senior Backend Engineer"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Job Posting Context
              </label>
              <textarea
                rows={3}
                value={qJobDesc}
                onChange={(e) => setQJobDesc(e.target.value)}
                placeholder="Paste key responsibilities or requirements..."
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <button
              onClick={() => handleExecuteTool("interview-questions", { job_title: qJobTitle || undefined, job_description: qJobDesc || undefined, resume_skills: ["Python", "FastAPI", "PostgreSQL"] })}
              disabled={isLoading}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition"
            >
              {isLoading ? "Generating Questions..." : "Generate Interview Questions"}
            </button>
          </div>
        )}

        {/* 4. Interview Prep Guide Form */}
        {activeSubTool === "prep" && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Target Job Title <span className="text-rose-400">*</span>
              </label>
              <input
                type="text"
                value={prepJobTitle}
                onChange={(e) => setPrepJobTitle(e.target.value)}
                placeholder="e.g. Backend Engineer (Python / FastAPI)"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Required Job Skills (comma-separated)
                </label>
                <input
                  type="text"
                  value={prepReqSkills}
                  onChange={(e) => setPrepReqSkills(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Missing Skills to Study (comma-separated)
                </label>
                <input
                  type="text"
                  value={prepMissSkills}
                  onChange={(e) => setPrepMissSkills(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
            <button
              onClick={() => handleExecuteTool("interview-prep", {
                job_title: prepJobTitle,
                required_skills: prepReqSkills.split(",").map(s => s.trim()).filter(Boolean),
                missing_skills: prepMissSkills.split(",").map(s => s.trim()).filter(Boolean),
              })}
              disabled={isLoading || !prepJobTitle.trim()}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition"
            >
              {isLoading ? "Building Prep Guide..." : "Generate Prep Guide"}
            </button>
          </div>
        )}

        {/* 5. Tech Explainer Form */}
        {activeSubTool === "tech" && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Technology Name <span className="text-rose-400">*</span>
              </label>
              <input
                type="text"
                value={techName}
                onChange={(e) => setTechName(e.target.value)}
                placeholder="e.g. Docker, PostgreSQL, Redis"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Job Context
              </label>
              <input
                type="text"
                value={techJobContext}
                onChange={(e) => setTechJobContext(e.target.value)}
                placeholder="e.g. Backend Developer deploying microservices"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <button
              onClick={() => handleExecuteTool("explain-technology", { technology_name: techName, job_context: techJobContext || undefined })}
              disabled={isLoading || !techName.trim()}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition"
            >
              {isLoading ? "Explaining Technology..." : "Explain Technology"}
            </button>
          </div>
        )}

        {/* 6. Study Plan Generator Form */}
        {activeSubTool === "study" && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Missing Skills to Master (comma-separated) <span className="text-rose-400">*</span>
              </label>
              <input
                type="text"
                value={planMissingSkills}
                onChange={(e) => setPlanMissingSkills(e.target.value)}
                placeholder="e.g. Docker, Kubernetes, Redis"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Target Duration (Weeks)
              </label>
              <input
                type="number"
                min={1}
                max={12}
                value={planWeeks}
                onChange={(e) => setPlanWeeks(parseInt(e.target.value) || 4)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <button
              onClick={() => handleExecuteTool("study-plan", {
                missing_skills: planMissingSkills.split(",").map(s => s.trim()).filter(Boolean),
                available_weeks: planWeeks,
              })}
              disabled={isLoading || !planMissingSkills.trim()}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition"
            >
              {isLoading ? "Generating Study Plan..." : "Generate Study Plan"}
            </button>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Output Results Container */}
        {resultData && (
          <div className="mt-8 pt-6 border-t border-slate-800 space-y-6">
            <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider block">AI Career Output</span>

            {/* Bullet Result */}
            {activeSubTool === "bullet" && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                  <span className="text-xs text-slate-500 block">Improved Bullet Point:</span>
                  <p className="text-slate-100 font-semibold text-base">{resultData.improved_bullet}</p>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs text-slate-300 space-y-1">
                  <span className="font-semibold text-indigo-300 block">Enhancement Explanation:</span>
                  <p>{resultData.explanation}</p>
                </div>
                <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
                  <span>✓</span>
                  <span>{resultData.factual_note}</span>
                </div>
              </div>
            )}

            {/* Skill Result */}
            {activeSubTool === "skill" && (
              <div className="space-y-4 text-sm">
                <h3 className="text-xl font-bold text-white">{resultData.skill_name} Overview</h3>
                <p className="text-slate-300 bg-slate-950 p-4 rounded-xl border border-slate-800">{resultData.summary}</p>
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="font-semibold text-indigo-300 text-xs block uppercase mb-2">Why Relevant:</span>
                  <p className="text-slate-300">{resultData.why_relevant}</p>
                </div>
                <div>
                  <span className="font-semibold text-slate-300 text-xs uppercase block mb-2">Core Concepts:</span>
                  <div className="flex flex-wrap gap-2">
                    {resultData.core_concepts?.map((c: string, i: number) => (
                      <span key={i} className="px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 text-xs">{c}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Interview Questions Result */}
            {activeSubTool === "questions" && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-white">Questions for {resultData.job_title}</h3>
                <div className="space-y-3">
                  {resultData.questions?.map((q: any, i: number) => (
                    <div key={i} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">{q.category}</span>
                      </div>
                      <p className="text-slate-100 font-semibold text-sm">{q.question}</p>
                      <p className="text-xs text-slate-400">💡 Tip: {q.tip_or_context}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Prep Guide Result */}
            {activeSubTool === "prep" && (
              <div className="space-y-4 text-sm">
                <h3 className="text-lg font-bold text-white">Preparation Strategy for {resultData.job_title}</h3>
                <p className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">{resultData.prep_strategy}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                    <span className="font-semibold text-xs text-indigo-400 uppercase block mb-2">Topics to Revise</span>
                    <ul className="list-disc list-inside space-y-1 text-xs text-slate-300">
                      {resultData.revision_topics?.map((t: string, i: number) => <li key={i}>{t}</li>)}
                    </ul>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                    <span className="font-semibold text-xs text-purple-400 uppercase block mb-2">Likely Technical Areas</span>
                    <ul className="list-disc list-inside space-y-1 text-xs text-slate-300">
                      {resultData.technical_focus_areas?.map((t: string, i: number) => <li key={i}>{t}</li>)}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Tech Result */}
            {activeSubTool === "tech" && (
              <div className="space-y-4 text-sm">
                <h3 className="text-xl font-bold text-white">{resultData.technology_name} Explanation</h3>
                <p className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">{resultData.simple_explanation}</p>
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-xs font-semibold text-indigo-400 uppercase block mb-2">Role Relevance:</span>
                  <p className="text-xs text-slate-300">{resultData.relevance_to_role}</p>
                </div>
              </div>
            )}

            {/* Study Plan Result */}
            {activeSubTool === "study" && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-white">{resultData.total_weeks}-Week Learning Roadmap</h3>
                <div className="space-y-4">
                  {resultData.weekly_plan?.map((w: any, i: number) => (
                    <div key={i} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                      <span className="text-xs font-bold text-indigo-400 uppercase">Week {w.week_number}: {w.focus_area}</span>
                      <ul className="list-disc list-inside text-xs text-slate-300">
                        {w.topics?.map((t: string, j: number) => <li key={j}>{t}</li>)}
                      </ul>
                      <div className="text-xs font-medium text-emerald-400 pt-1">🎯 Milestone: {w.practical_milestone}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
