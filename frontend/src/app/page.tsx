"use client";

import { useEffect, useState } from "react";
import ResumeUpload from "@/components/ResumeUpload";
import JobAnalyzer from "@/components/JobAnalyzer";
import MatchAnalyzer from "@/components/MatchAnalyzer";
import ApplicationTracker from "@/components/ApplicationTracker";
import CareerAssistant from "@/components/CareerAssistant";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"resume" | "job" | "matching" | "tracker" | "career">("career");
  const [healthStatus, setHealthStatus] = useState<"checking" | "online" | "offline">("checking");

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch("http://localhost:8000/health");
        if (res.ok) {
          setHealthStatus("online");
        } else {
          setHealthStatus("offline");
        }
      } catch (err) {
        setHealthStatus("offline");
      }
    };
    checkBackend();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      {/* Header / Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
              JM
            </div>
            <span className="font-bold text-xl tracking-tight text-white">
              JobMatch <span className="text-indigo-400">AI</span>
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
              Phase 6 Active
            </span>
            <div className="flex items-center space-x-2 text-xs">
              <span className={`w-2.5 h-2.5 rounded-full ${healthStatus === "online" ? "bg-emerald-400 animate-pulse" : healthStatus === "offline" ? "bg-rose-500" : "bg-amber-400 animate-ping"}`} />
              <span className="text-slate-400">
                Backend: <span className={healthStatus === "online" ? "text-emerald-400 font-semibold" : healthStatus === "offline" ? "text-rose-400 font-semibold" : "text-amber-400"}>
                  {healthStatus === "online" ? "Online" : healthStatus === "offline" ? "Offline" : "Checking..."}
                </span>
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-10 flex-1 flex flex-col items-center w-full space-y-8">
        {/* Navigation Tabs */}
        <div className="flex flex-wrap justify-center p-1.5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg gap-1">
          <button
            onClick={() => setActiveTab("resume")}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition flex items-center space-x-2 ${activeTab === "resume"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white"
              }`}
          >
            <span>📄 Resume Intelligence</span>
            <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-slate-950/60 border border-slate-700">P2</span>
          </button>
          <button
            onClick={() => setActiveTab("job")}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition flex items-center space-x-2 ${activeTab === "job"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white"
              }`}
          >
            <span>🎯 Job Intelligence</span>
            <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-slate-950/60 border border-slate-700">P3</span>
          </button>
          <button
            onClick={() => setActiveTab("matching")}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition flex items-center space-x-2 ${activeTab === "matching"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white"
              }`}
          >
            <span>⚡ Resume ↔ Job Match</span>
            <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-slate-950/60 border border-slate-700">P4</span>
          </button>
          <button
            onClick={() => setActiveTab("tracker")}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition flex items-center space-x-2 ${activeTab === "tracker"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white"
              }`}
          >
            <span>📊 Application Tracker</span>
            <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-slate-950/60 border border-slate-700">P5</span>
          </button>
          <button
            onClick={() => setActiveTab("career")}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition flex items-center space-x-2 ${activeTab === "career"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white"
              }`}
          >
            <span>🤖 AI Career Assistant</span>
            <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-slate-950/60 border border-slate-700">P6</span>
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === "resume" ? (
          <div className="w-full space-y-8">
            <div className="text-center max-w-3xl mx-auto space-y-3">
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                Instant Resume Analysis & Parsing
              </h1>
              <p className="text-slate-400 text-sm sm:text-base">
                Upload your resume in PDF or DOCX format to extract structured contact details, skills, education, and experience.
              </p>
            </div>
            <ResumeUpload />
          </div>
        ) : activeTab === "job" ? (
          <div className="w-full space-y-8">
            <div className="text-center max-w-3xl mx-auto space-y-3">
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                Job Description Intelligence & Requirement Extractor
              </h1>
              <p className="text-slate-400 text-sm sm:text-base">
                Paste any job description text to automatically extract required skills, preferred qualifications, technologies, education, experience, and keywords using Gemini AI.
              </p>
            </div>
            <JobAnalyzer />
          </div>
        ) : activeTab === "matching" ? (
          <div className="w-full space-y-8">
            <div className="text-center max-w-3xl mx-auto space-y-3">
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                Explainable Resume ↔ Job Compatibility Matching Engine
              </h1>
              <p className="text-slate-400 text-sm sm:text-base">
                Evaluate skill overlaps, missing required/preferred skills, technology matches, education compatibility, and experience alignment with zero arbitrary percentage guesswork.
              </p>
            </div>
            <MatchAnalyzer />
          </div>
        ) : activeTab === "tracker" ? (
          <div className="w-full space-y-8">
            <div className="text-center max-w-3xl mx-auto space-y-3">
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                Job Application Tracker & Pipeline Dashboard
              </h1>
              <p className="text-slate-400 text-sm sm:text-base">
                Keep track of jobs you are interested in or have applied for, update interview dates, and monitor your application metrics.
              </p>
            </div>
            <ApplicationTracker />
          </div>
        ) : (
          <div className="w-full space-y-8">
            <div className="text-center max-w-3xl mx-auto space-y-3">
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                AI Career Assistant & Growth Toolkit
              </h1>
              <p className="text-slate-400 text-sm sm:text-base">
                Enhance resume bullet points, explain missing technical skills, generate practice interview questions, build job interview prep guides, and create week-by-week study plans using Gemini AI.
              </p>
            </div>
            <CareerAssistant />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-8 text-center text-xs text-slate-500">
        JobMatch AI — Phase 6: AI Career Assistant
      </footer>
    </div>
  );
}