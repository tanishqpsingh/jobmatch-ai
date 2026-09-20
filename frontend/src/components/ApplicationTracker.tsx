"use client";

import React, { useEffect, useState } from "react";

export type ApplicationStatusType = "saved" | "applied" | "screening" | "interview" | "offer" | "rejected" | "withdrawn";

export interface ApplicationItem {
  id: number;
  company: string;
  job_title: string;
  job_description?: string | null;
  application_date?: string | null;
  status: ApplicationStatusType;
  interview_date?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationSummary {
  total: number;
  saved: number;
  applied: number;
  screening: number;
  interview: number;
  offer: number;
  rejected: number;
  withdrawn: number;
}

export default function ApplicationTracker() {
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [summary, setSummary] = useState<ApplicationSummary>({
    total: 0,
    saved: 0,
    applied: 0,
    screening: 0,
    interview: 0,
    offer: 0,
    rejected: 0,
    withdrawn: 0,
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Form Modals State
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [editingApp, setEditingApp] = useState<ApplicationItem | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  // Form Fields State
  const [formCompany, setFormCompany] = useState<string>("");
  const [formJobTitle, setFormJobTitle] = useState<string>("");
  const [formStatus, setFormStatus] = useState<ApplicationStatusType>("applied");
  const [formAppDate, setFormAppDate] = useState<string>(new Date().toISOString().split("T")[0]);
  const [formInterviewDate, setFormInterviewDate] = useState<string>("");
  const [formNotes, setFormNotes] = useState<string>("");
  const [formJobDesc, setFormJobDesc] = useState<string>("");
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const fetchApplicationsAndSummary = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [appsRes, summaryRes] = await Promise.all([
        fetch("http://localhost:8000/api/v1/applications"),
        fetch("http://localhost:8000/api/v1/applications/summary"),
      ]);

      if (!appsRes.ok || !summaryRes.ok) {
        throw new Error("Failed to load application data from server.");
      }

      const appsData: ApplicationItem[] = await appsRes.json();
      const summaryData: ApplicationSummary = await summaryRes.json();

      setApplications(appsData);
      setSummary(summaryData);
    } catch (err: any) {
      setError(err.message || "Error fetching applications.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchApplicationsAndSummary();
  }, []);

  const resetForm = () => {
    setFormCompany("");
    setFormJobTitle("");
    setFormStatus("applied");
    setFormAppDate(new Date().toISOString().split("T")[0]);
    setFormInterviewDate("");
    setFormNotes("");
    setFormJobDesc("");
    setFormError(null);
    setEditingApp(null);
  };

  const handleOpenAddModal = () => {
    resetForm();
    setIsAddModalOpen(true);
  };

  const handleOpenEditModal = (app: ApplicationItem) => {
    setEditingApp(app);
    setFormCompany(app.company);
    setFormJobTitle(app.job_title);
    setFormStatus(app.status);
    setFormAppDate(app.application_date || "");
    setFormInterviewDate(app.interview_date ? app.interview_date.slice(0, 16) : "");
    setFormNotes(app.notes || "");
    setFormJobDesc(app.job_description || "");
    setFormError(null);
    setIsAddModalOpen(true);
  };

  const handleSaveApplication = async () => {
    if (!formCompany.trim()) {
      setFormError("Company name is required.");
      return;
    }
    if (!formJobTitle.trim()) {
      setFormError("Job title is required.");
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    const payload = {
      company: formCompany.trim(),
      job_title: formJobTitle.trim(),
      status: formStatus,
      application_date: formAppDate || null,
      interview_date: formInterviewDate ? new Date(formInterviewDate).toISOString() : null,
      notes: formNotes.trim() || null,
      job_description: formJobDesc.trim() || null,
    };

    try {
      let url = "http://localhost:8000/api/v1/applications";
      let method = "POST";

      if (editingApp) {
        url = `http://localhost:8000/api/v1/applications/${editingApp.id}`;
        method = "PATCH";
      }

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || "Failed to save application.");
      }

      setIsAddModalOpen(false);
      resetForm();
      await fetchApplicationsAndSummary();
    } catch (err: any) {
      setFormError(err.message || "An error occurred while saving.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickStatusChange = async (appId: number, newStatus: ApplicationStatusType) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/applications/${appId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        await fetchApplicationsAndSummary();
      }
    } catch (err) {
      console.error("Status update failed", err);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingId) return;

    try {
      const res = await fetch(`http://localhost:8000/api/v1/applications/${deletingId}`, {
        method: "DELETE",
      });
      if (res.ok) {
        setDeletingId(null);
        await fetchApplicationsAndSummary();
      } else {
        alert("Failed to delete application.");
      }
    } catch (err) {
      alert("Error deleting application.");
    }
  };

  const getStatusBadge = (status: ApplicationStatusType) => {
    switch (status) {
      case "saved":
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">SAVED</span>;
      case "applied":
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">APPLIED</span>;
      case "screening":
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">SCREENING</span>;
      case "interview":
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20">INTERVIEW</span>;
      case "offer":
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">OFFER 🎉</span>;
      case "rejected":
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-300 border border-rose-500/20">REJECTED</span>;
      case "withdrawn":
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400">WITHDRAWN</span>;
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-8">
      {/* Summary Metrics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
          <span className="text-slate-400 text-xs font-medium block uppercase tracking-wider">Total</span>
          <span className="text-2xl font-extrabold text-white mt-1 block">{summary.total}</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
          <span className="text-indigo-400 text-xs font-medium block uppercase tracking-wider">Applied</span>
          <span className="text-2xl font-extrabold text-indigo-300 mt-1 block">{summary.applied}</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
          <span className="text-amber-400 text-xs font-medium block uppercase tracking-wider">Interviews</span>
          <span className="text-2xl font-extrabold text-amber-300 mt-1 block">{summary.interview}</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
          <span className="text-emerald-400 text-xs font-medium block uppercase tracking-wider">Offers</span>
          <span className="text-2xl font-extrabold text-emerald-300 mt-1 block">{summary.offer}</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center col-span-2 sm:col-span-4 md:col-span-1">
          <span className="text-rose-400 text-xs font-medium block uppercase tracking-wider">Rejected</span>
          <span className="text-2xl font-extrabold text-rose-300 mt-1 block">{summary.rejected}</span>
        </div>
      </div>

      {/* Main Table Container */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 backdrop-blur shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              Tracked Job Applications
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Organize and track your job application pipeline status, interview schedules, and notes.
            </p>
          </div>
          <button
            onClick={handleOpenAddModal}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition shadow-lg shadow-indigo-600/20 flex items-center gap-2 self-start sm:self-auto"
          >
            <span>+ Add Application</span>
          </button>
        </div>

        {error && (
          <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Applications List */}
        {isLoading ? (
          <div className="py-12 text-center text-slate-400 text-sm flex flex-col items-center gap-3">
            <div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
            <span>Loading database records...</span>
          </div>
        ) : applications.length === 0 ? (
          <div className="py-16 text-center text-slate-500 text-sm space-y-3">
            <div className="text-3xl">📥</div>
            <div className="font-semibold text-slate-300">No applications tracked yet</div>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Click "+ Add Application" above to track a job posting you have saved or applied for.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/60 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Company & Role</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">App Date</th>
                  <th className="px-4 py-3">Interview Date</th>
                  <th className="px-4 py-3">Notes</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-4 py-3">
                      <div className="font-bold text-white">{app.job_title}</div>
                      <div className="text-xs text-slate-400">{app.company}</div>
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={app.status}
                        onChange={(e) => handleQuickStatusChange(app.id, e.target.value as ApplicationStatusType)}
                        className="bg-slate-950 border border-slate-800 rounded-lg text-xs py-1 px-2 text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
                      >
                        <option value="saved">Saved</option>
                        <option value="applied">Applied</option>
                        <option value="screening">Screening</option>
                        <option value="interview">Interview</option>
                        <option value="offer">Offer</option>
                        <option value="rejected">Rejected</option>
                        <option value="withdrawn">Withdrawn</option>
                      </select>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {app.application_date || "—"}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {app.interview_date ? new Date(app.interview_date).toLocaleDateString() : "—"}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400 max-w-xs truncate">
                      {app.notes || "—"}
                    </td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <button
                        onClick={() => handleOpenEditModal(app)}
                        className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => setDeletingId(app.id)}
                        className="text-xs font-semibold text-rose-400 hover:text-rose-300 transition"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add / Edit Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">
                {editingApp ? "Edit Application" : "Track New Application"}
              </h3>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {formError && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
                ⚠️ {formError}
              </div>
            )}

            <div className="space-y-4 text-sm">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Company Name <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Acme Corporation"
                  value={formCompany}
                  onChange={(e) => setFormCompany(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Job Title <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Senior Backend Engineer"
                  value={formJobTitle}
                  onChange={(e) => setFormJobTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                    Status
                  </label>
                  <select
                    value={formStatus}
                    onChange={(e) => setFormStatus(e.target.value as ApplicationStatusType)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
                  >
                    <option value="saved">Saved</option>
                    <option value="applied">Applied</option>
                    <option value="screening">Screening</option>
                    <option value="interview">Interview</option>
                    <option value="offer">Offer</option>
                    <option value="rejected">Rejected</option>
                    <option value="withdrawn">Withdrawn</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                    Application Date
                  </label>
                  <input
                    type="date"
                    value={formAppDate}
                    onChange={(e) => setFormAppDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Scheduled Interview Date <span className="text-slate-500 lowercase">(optional)</span>
                </label>
                <input
                  type="datetime-local"
                  value={formInterviewDate}
                  onChange={(e) => setFormInterviewDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Notes <span className="text-slate-500 lowercase">(optional)</span>
                </label>
                <textarea
                  rows={3}
                  placeholder="Referral name, salary range, recruiter contact, etc."
                  value={formNotes}
                  onChange={(e) => setFormNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                onClick={handleSaveApplication}
                disabled={isSubmitting}
                className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition"
              >
                {isSubmitting ? "Saving..." : editingApp ? "Update Record" : "Save Record"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deletingId && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-sm w-full space-y-4 text-center">
            <div className="text-2xl">🗑️</div>
            <h3 className="text-lg font-bold text-white">Confirm Deletion</h3>
            <p className="text-xs text-slate-400">
              Are you sure you want to delete this tracked application? This action cannot be undone.
            </p>
            <div className="flex justify-center space-x-3 pt-2">
              <button
                onClick={() => setDeletingId(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold"
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
