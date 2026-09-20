"use client";

import React, { useState } from "react";
import { apiUrl } from "@/lib/api";

export interface JobAnalysisData {
  job_title: string | null;
  company: string | null;
  required_skills: string[];
  preferred_skills: string[];
  technologies: string[];
  education_requirements: string[];
  experience_requirements: string[];
  keywords: string[];
}

export default function JobAnalyzer() {
  const [jobDescription, setJobDescription] = useState<string>("");
  const [jobTitle, setJobTitle] = useState<string>("");
  const [company, setCompany] = useState<string>("");
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<JobAnalysisData | null>(null);

  const sampleJobText = `Senior Backend Engineer (Python / FastAPI)
Acme Technologies — Remote

We are looking for a Senior Backend Engineer to architect, build, and maintain our high-throughput APIs.

Key Responsibilities:
- Design and develop scalable asynchronous REST microservices using Python and FastAPI.
- Optimize complex database queries in PostgreSQL with SQLAlchemy and asyncpg.
- Containerize services using Docker and manage deployment pipelines.

Requirements:
- 5+ years of professional backend engineering experience.
- Strong proficiency in Python, FastAPI, and relational database schema design.
- Hands-on experience with Docker, CI/CD, and Cloud (AWS/GCP).
- Bachelor's degree in Computer Science, Software Engineering, or equivalent experience.

Nice-to-Have / Preferred:
- Experience integrating Google Gemini API or LLM AI agents.
- Experience with Redis caching and Celery task queues.`;

  const handleLoadSample = () => {
    setJobTitle("Senior Backend Engineer");
    setCompany("Acme Technologies");
    setJobDescription(sampleJobText);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!jobDescription.trim()) {
      setError("Please enter or paste a job description.");
      return;
    }

    if (jobDescription.trim().length < 10) {
      setError("Job description is too short (minimum 10 characters required).");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch(apiUrl("/api/v1/jobs/analyze"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_description: jobDescription,
          job_title: jobTitle.trim() || undefined,
          company: company.trim() || undefined,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `Analysis failed with status code ${response.status}`);
      }

      const data: JobAnalysisData = await response.json();
      setAnalysisResult(data);
    } catch (err: any) {
      setError(err.message || "An error occurred while analyzing the job description.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      {/* Input Form */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              Job Description Intelligence
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              Paste a job posting to extract required skills, technologies, education, experience, and key requirements.
            </p>
          </div>
          <button
            onClick={handleLoadSample}
            type="button"
            className="px-3 py-1.5 text-xs font-semibold text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 rounded-lg transition self-start sm:self-auto"
          >
            Load Sample Posting
          </button>
        </div>

        {/* Optional Metadata Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Job Title <span className="text-slate-500 font-normal lowercase">(optional)</span>
            </label>
            <input
              type="text"
              placeholder="e.g. Senior Backend Engineer"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500 transition"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Company Name <span className="text-slate-500 font-normal lowercase">(optional)</span>
            </label>
            <input
              type="text"
              placeholder="e.g. Acme Technologies"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500 transition"
            />
          </div>
        </div>

        {/* Job Description Textarea */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Job Description Text <span className="text-rose-400">*</span>
            </label>
            <span className="text-xs text-slate-500">{jobDescription.length} / 50,000 chars</span>
          </div>
          <textarea
            rows={8}
            placeholder="Paste the full job description text here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500 transition font-mono leading-relaxed"
          />
        </div>

        {error && (
          <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div className="flex items-center justify-end space-x-4 pt-2">
          {jobDescription && (
            <button
              onClick={() => {
                setJobDescription("");
                setJobTitle("");
                setCompany("");
                setAnalysisResult(null);
                setError(null);
              }}
              className="px-4 py-2 text-sm text-slate-400 hover:text-white transition"
              disabled={isAnalyzing}
            >
              Clear
            </button>
          )}

          <button
            onClick={handleAnalyze}
            disabled={!jobDescription.trim() || isAnalyzing}
            className={`px-6 py-2.5 rounded-xl font-semibold text-sm transition flex items-center space-x-2 ${
              !jobDescription.trim() || isAnalyzing
                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20"
            }`}
          >
            {isAnalyzing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Analyzing Job Description...</span>
              </>
            ) : (
              <span>Analyze Job Requirements</span>
            )}
          </button>
        </div>
      </div>

      {/* Analysis Results Display */}
      {analysisResult && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur shadow-xl space-y-6">
          <div className="border-b border-slate-800 pb-4">
            <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider">AI Extracted Requirements</span>
            <h3 className="text-2xl font-bold text-white mt-1">
              {analysisResult.job_title || "Unspecified Role"}
              {analysisResult.company && <span className="text-slate-400 font-normal"> at {analysisResult.company}</span>}
            </h3>
          </div>

          <div className="space-y-6">
            {/* Required Skills */}
            {analysisResult.required_skills.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-rose-400" />
                  Required Skills
                </h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.required_skills.map((skill, i) => (
                    <span key={i} className="px-3 py-1 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs font-medium">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Preferred Skills */}
            {analysisResult.preferred_skills.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                  Preferred / Nice-to-Have Skills
                </h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.preferred_skills.map((skill, i) => (
                    <span key={i} className="px-3 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-medium">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Technologies */}
            {analysisResult.technologies.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-indigo-400" />
                  Technologies & Tools
                </h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.technologies.map((tech, i) => (
                    <span key={i} className="px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Experience Requirements */}
            {analysisResult.experience_requirements.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Experience Requirements</h4>
                <ul className="space-y-2">
                  {analysisResult.experience_requirements.map((exp, i) => (
                    <li key={i} className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 text-slate-300 text-sm">
                      {exp}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Education Requirements */}
            {analysisResult.education_requirements.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Education Requirements</h4>
                <ul className="space-y-2">
                  {analysisResult.education_requirements.map((edu, i) => (
                    <li key={i} className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 text-slate-300 text-sm">
                      {edu}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Keywords */}
            {analysisResult.keywords.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Core Industry Keywords</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.keywords.map((kw, i) => (
                    <span key={i} className="px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 text-xs font-mono">
                      #{kw}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
