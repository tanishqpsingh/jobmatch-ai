"use client";

import React, { useState } from "react";
import { apiUrl } from "@/lib/api";
import { ResumeData } from "./ResumeUpload";
import { JobAnalysisData } from "./JobAnalyzer";

export interface CompatibilityAnalysis {
  status: "match" | "partial_match" | "mismatch" | "insufficient_information";
  details: string;
}

export interface MatchAnalysisData {
  matching_skills: string[];
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  matching_technologies: string[];
  missing_technologies: string[];
  education_analysis: CompatibilityAnalysis;
  experience_analysis: CompatibilityAnalysis;
  matching_keywords: string[];
  missing_keywords: string[];
  summary: string;
}

interface MatchAnalyzerProps {
  sampleResume?: ResumeData;
  sampleJob?: JobAnalysisData;
}

export default function MatchAnalyzer({ sampleResume, sampleJob }: MatchAnalyzerProps) {
  const defaultResume: ResumeData = sampleResume || {
    filename: "jane_doe_resume.pdf",
    name: "Jane Doe",
    email: "jane.doe@example.com",
    phone: "(555) 123-4567",
    education: ["Bachelor of Science in Computer Science"],
    skills: ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "REST APIs"],
    experience: [
      "Senior Software Engineer at Tech Corp (3 years)",
      "Backend Developer at Startup (2 years)",
    ],
    projects: ["JobMatch AI Platform"],
    certifications: ["AWS Certified Cloud Practitioner"],
    raw_text: "Jane Doe. BS in Computer Science. 5 years experience with Python, FastAPI, PostgreSQL, Docker, Git.",
  };

  const defaultJob: JobAnalysisData = sampleJob || {
    job_title: "Senior Backend Engineer",
    company: "Acme Technologies",
    required_skills: ["Python", "FastAPI", "PostgreSQL", "Kubernetes"],
    preferred_skills: ["AWS", "Redis", "GraphQL"],
    technologies: ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
    education_requirements: ["Bachelor of Science in Computer Science or related field"],
    experience_requirements: ["3+ years of backend engineering experience"],
    keywords: ["Backend", "Microservices", "REST APIs", "Containerization"],
  };

  const [resumeData, setResumeData] = useState<ResumeData>(defaultResume);
  const [jobData, setJobData] = useState<JobAnalysisData>(defaultJob);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [matchResult, setMatchResult] = useState<MatchAnalysisData | null>(null);

  const handleAnalyzeMatch = async () => {
    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch(apiUrl("/api/v1/matching/analyze"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume: resumeData,
          job: jobData,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `Matching analysis failed with status ${response.status}`);
      }

      const data: MatchAnalysisData = await response.json();
      setMatchResult(data);
    } catch (err: any) {
      setError(err.message || "An error occurred while computing resume-job match.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getStatusBadge = (status: CompatibilityAnalysis["status"]) => {
    switch (status) {
      case "match":
        return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">MATCH</span>;
      case "partial_match":
        return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">PARTIAL MATCH</span>;
      case "mismatch":
        return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">MISMATCH</span>;
      case "insufficient_information":
      default:
        return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">INSUFFICIENT DATA</span>;
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      {/* Input Summary Cards */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
              </svg>
              Resume ↔ Job Compatibility Matching Engine
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              Compare candidate qualifications against target job requirements for explainable skill, technology, education, and experience compatibility.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
          {/* Active Resume Context */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
            <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider block">Candidate Resume</span>
            <div className="font-bold text-white">{resumeData.name || "Unnamed Candidate"}</div>
            <div className="text-xs text-slate-400">Skills: {resumeData.skills.join(", ") || "None extracted"}</div>
          </div>

          {/* Active Job Context */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
            <span className="text-xs font-semibold text-purple-400 uppercase tracking-wider block">Target Job Description</span>
            <div className="font-bold text-white">{jobData.job_title || "Unspecified Role"} {jobData.company && `at ${jobData.company}`}</div>
            <div className="text-xs text-slate-400">Required Skills: {jobData.required_skills.join(", ") || "None extracted"}</div>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div className="flex justify-end pt-2">
          <button
            onClick={handleAnalyzeMatch}
            disabled={isAnalyzing}
            className={`px-6 py-2.5 rounded-xl font-semibold text-sm transition flex items-center space-x-2 ${
              isAnalyzing
                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20"
            }`}
          >
            {isAnalyzing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Computing Match Breakdown...</span>
              </>
            ) : (
              <span>Analyze Match Breakdown</span>
            )}
          </button>
        </div>
      </div>

      {/* Match Results Display */}
      {matchResult && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur shadow-xl space-y-8">
          <div className="border-b border-slate-800 pb-4">
            <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider">Explainable Comparison Output</span>
            <h3 className="text-2xl font-bold text-white mt-1">Match Breakdown Summary</h3>
            <p className="mt-3 p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 text-sm leading-relaxed">
              {matchResult.summary}
            </p>
          </div>

          {/* Grid of Match Analysis Categories */}
          <div className="space-y-6">
            {/* Required Skills Match vs Missing */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-5 rounded-xl bg-slate-950/40 border border-slate-800">
                <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  Matching Skills ({matchResult.matching_skills.length})
                </h4>
                {matchResult.matching_skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {matchResult.matching_skills.map((skill, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-medium">
                        ✓ {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 text-xs">No required skill matches detected.</p>
                )}
              </div>

              <div className="p-5 rounded-xl bg-slate-950/40 border border-slate-800">
                <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-rose-400" />
                  Missing Required Skills ({matchResult.missing_required_skills.length})
                </h4>
                {matchResult.missing_required_skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {matchResult.missing_required_skills.map((skill, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs font-medium">
                        ✗ {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-emerald-400 text-xs font-medium">✓ Candidate possesses all required skills!</p>
                )}
              </div>
            </div>

            {/* Preferred Skills & Technologies */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-5 rounded-xl bg-slate-950/40 border border-slate-800">
                <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-3">
                  Missing Preferred Skills ({matchResult.missing_preferred_skills.length})
                </h4>
                {matchResult.missing_preferred_skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {matchResult.missing_preferred_skills.map((skill, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-medium">
                        ! {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-400 text-xs">No missing preferred skills.</p>
                )}
              </div>

              <div className="p-5 rounded-xl bg-slate-950/40 border border-slate-800">
                <h4 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-3">
                  Technology Overlap ({matchResult.matching_technologies.length})
                </h4>
                {matchResult.matching_technologies.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {matchResult.matching_technologies.map((tech, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium">
                        {tech}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 text-xs">No technology overlaps found.</p>
                )}
              </div>
            </div>

            {/* Education & Experience Compatibility Analysis */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-5 rounded-xl bg-slate-950/40 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Education Compatibility</h4>
                  {getStatusBadge(matchResult.education_analysis.status)}
                </div>
                <p className="text-slate-400 text-xs leading-relaxed">
                  {matchResult.education_analysis.details}
                </p>
              </div>

              <div className="p-5 rounded-xl bg-slate-950/40 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Experience Compatibility</h4>
                  {getStatusBadge(matchResult.experience_analysis.status)}
                </div>
                <p className="text-slate-400 text-xs leading-relaxed">
                  {matchResult.experience_analysis.details}
                </p>
              </div>
            </div>

            {/* Keywords Match */}
            {matchResult.matching_keywords.length > 0 && (
              <div className="p-5 rounded-xl bg-slate-950/40 border border-slate-800">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">Matching Domain Keywords</h4>
                <div className="flex flex-wrap gap-2">
                  {matchResult.matching_keywords.map((kw, i) => (
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
