"use client";

import React, { useState, ChangeEvent, DragEvent } from "react";
import { apiUrl } from "@/lib/api";

export interface ResumeData {
  filename: string;
  name: string | null;
  email: string | null;
  phone: string | null;
  education: string[];
  skills: string[];
  experience: string[];
  projects: string[];
  certifications: string[];
  raw_text: string;
}

export default function ResumeUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [parsedData, setParsedData] = useState<ResumeData | null>(null);
  const [activeTab, setActiveTab] = useState<"structured" | "raw">("structured");
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const validateAndSetFile = (selectedFile: File) => {
    setError(null);
    const validExtensions = [".pdf", ".docx"];
    const ext = selectedFile.name.substring(selectedFile.name.lastIndexOf(".")).toLowerCase();

    if (!validExtensions.includes(ext)) {
      setError(`Unsupported file format '${ext}'. Please upload a PDF or DOCX document.`);
      setFile(null);
      return false;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setError("File size exceeds 5 MB limit.");
      setFile(null);
      return false;
    }

    if (selectedFile.size === 0) {
      setError("Selected file is empty (0 bytes).");
      setFile(null);
      return false;
    }

    setFile(selectedFile);
    return true;
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(apiUrl("/api/v1/resumes/parse"), {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `Upload failed with status code ${response.status}`);
      }

      const data: ResumeData = await response.json();
      setParsedData(data);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred during resume parsing.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      {/* Upload Zone */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur shadow-xl">
        <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
          <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 0115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Upload Resume (PDF / DOCX)
        </h2>
        <p className="text-sm text-slate-400 mb-6">
          Upload your resume document to securely extract structured contact details, skills, education, and experience.
        </p>

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition cursor-pointer flex flex-col items-center justify-center min-h-[180px] ${
            isDragging
              ? "border-indigo-400 bg-indigo-500/10"
              : file
              ? "border-emerald-500/50 bg-emerald-500/5"
              : "border-slate-700 hover:border-slate-600 bg-slate-950/40"
          }`}
        >
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            className="hidden"
            id="resume-file-input"
          />

          <label htmlFor="resume-file-input" className="cursor-pointer w-full h-full flex flex-col items-center justify-center">
            {file ? (
              <div className="flex flex-col items-center space-y-2">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
                  ✓
                </div>
                <span className="font-semibold text-slate-200">{file.name}</span>
                <span className="text-xs text-slate-400">{(file.size / 1024).toFixed(1)} KB</span>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="w-12 h-12 mx-auto rounded-full bg-slate-800 text-slate-400 flex items-center justify-center">
                  📄
                </div>
                <div>
                  <span className="text-indigo-400 font-medium hover:underline">Click to browse</span> or drag and drop your file here
                </div>
                <p className="text-xs text-slate-500">Supports PDF and DOCX up to 5 MB</p>
              </div>
            )}
          </label>
        </div>

        {error && (
          <div className="mt-4 p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div className="mt-6 flex items-center justify-end space-x-4">
          {file && (
            <button
              onClick={() => {
                setFile(null);
                setParsedData(null);
                setError(null);
              }}
              className="px-4 py-2 text-sm text-slate-400 hover:text-white transition"
              disabled={isUploading}
            >
              Clear
            </button>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className={`px-6 py-2.5 rounded-xl font-semibold text-sm transition flex items-center space-x-2 ${
              !file || isUploading
                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20"
            }`}
          >
            {isUploading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Processing Document...</span>
              </>
            ) : (
              <span>Extract & Parse Resume</span>
            )}
          </button>
        </div>
      </div>

      {/* Extracted Data View */}
      {parsedData && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur shadow-xl space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-4 gap-4">
            <div>
              <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider">Parsed Resume Output</span>
              <h3 className="text-2xl font-bold text-white mt-1">{parsedData.name || "Unnamed Candidate"}</h3>
            </div>
            <div className="flex space-x-2 bg-slate-950 p-1 rounded-lg border border-slate-800">
              <button
                onClick={() => setActiveTab("structured")}
                className={`px-4 py-1.5 rounded-md text-xs font-semibold transition ${
                  activeTab === "structured" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                Structured Data
              </button>
              <button
                onClick={() => setActiveTab("raw")}
                className={`px-4 py-1.5 rounded-md text-xs font-semibold transition ${
                  activeTab === "raw" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                Raw Normalized Text
              </button>
            </div>
          </div>

          {activeTab === "structured" ? (
            <div className="space-y-6">
              {/* Contact Card */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 text-sm">
                <div>
                  <span className="text-slate-500 block text-xs">Full Name</span>
                  <span className="text-slate-200 font-medium">{parsedData.name || "Not extracted"}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-xs">Email Address</span>
                  <span className="text-slate-200 font-medium">{parsedData.email || "Not extracted"}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-xs">Phone Number</span>
                  <span className="text-slate-200 font-medium">{parsedData.phone || "Not extracted"}</span>
                </div>
              </div>

              {/* Skills */}
              {parsedData.skills.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Extracted Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {parsedData.skills.map((skill, i) => (
                      <span key={i} className="px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Education */}
              {parsedData.education.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Education</h4>
                  <ul className="space-y-2">
                    {parsedData.education.map((item, i) => (
                      <li key={i} className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 text-slate-300 text-sm">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Experience */}
              {parsedData.experience.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Professional Experience</h4>
                  <ul className="space-y-2">
                    {parsedData.experience.map((item, i) => (
                      <li key={i} className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 text-slate-300 text-sm">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Projects */}
              {parsedData.projects.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Projects</h4>
                  <ul className="space-y-2">
                    {parsedData.projects.map((item, i) => (
                      <li key={i} className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 text-slate-300 text-sm">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Certifications */}
              {parsedData.certifications.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Certifications</h4>
                  <ul className="space-y-2">
                    {parsedData.certifications.map((item, i) => (
                      <li key={i} className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 text-slate-300 text-sm">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 whitespace-pre-wrap overflow-x-auto max-h-96">
              {parsedData.raw_text}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
