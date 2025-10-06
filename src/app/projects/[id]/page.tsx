"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import {
  projectAPI,
  datasetAPI,
  trainingAPI,
  type Project,
  type Dataset,
  type TrainingRun,
  type FederatedLearningStatus,
} from "@/lib/api";

export default function ProjectPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = Number(params.id);

  const [project, setProject] = useState<Project | null>(null);
  const [federatedStatus, setFederatedStatus] =
    useState<FederatedLearningStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<
    "datasets" | "federated" | "members"
  >("datasets");
  const [showUploadModal, setShowUploadModal] = useState(false);

  useEffect(() => {
    loadProjectData();
  }, [projectId]);

  const loadProjectData = async () => {
    try {
      const [projectRes, federatedRes] = await Promise.all([
        projectAPI.get(projectId),
        projectAPI.getFederatedStatus(projectId),
      ]);

      setProject(projectRes.data.project);
      setFederatedStatus(federatedRes.data);
    } catch (error) {
      console.error("Error loading project:", error);
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading project...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link
              href="/dashboard"
              className="text-gray-600 hover:text-gray-900"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {project.name}
              </h1>
              <p className="text-sm text-gray-600">Code: {project.code}</p>
            </div>
          </div>
          <button
            onClick={() => setShowUploadModal(true)}
            className="btn btn-primary"
          >
            <svg
              className="w-5 h-5 inline-block mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            Upload Dataset
          </button>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab("datasets")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "datasets"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              My Datasets
            </button>
            <button
              onClick={() => setActiveTab("federated")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "federated"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Federated Learning
            </button>
            <button
              onClick={() => setActiveTab("members")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "members"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Members ({project.members?.length || 0})
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "datasets" && (
          <DatasetsTab
            datasets={project.datasets || []}
            onRefresh={loadProjectData}
          />
        )}
        {activeTab === "federated" && federatedStatus && (
          <FederatedTab federatedStatus={federatedStatus} />
        )}
        {activeTab === "members" && (
          <MembersTab members={project.members || []} />
        )}
      </main>

      {/* Upload Modal */}
      {showUploadModal && (
        <UploadDatasetModal
          projectId={projectId}
          onClose={() => setShowUploadModal(false)}
          onSuccess={() => {
            setShowUploadModal(false);
            loadProjectData();
          }}
        />
      )}
    </div>
  );
}

function DatasetsTab({
  datasets,
  onRefresh,
}: {
  datasets: Dataset[];
  onRefresh: () => void;
}) {
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);

  if (datasets.length === 0) {
    return (
      <div className="card text-center py-12">
        <svg
          className="w-16 h-16 text-gray-400 mx-auto mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No datasets uploaded yet
        </h3>
        <p className="text-gray-600">
          Upload a dataset to start training models
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {datasets.map((dataset) => (
        <DatasetCard
          key={dataset.id}
          dataset={dataset}
          onRefresh={onRefresh}
          isExpanded={selectedDataset?.id === dataset.id}
          onToggle={() =>
            setSelectedDataset(
              selectedDataset?.id === dataset.id ? null : dataset
            )
          }
        />
      ))}
    </div>
  );
}

function DatasetCard({
  dataset,
  onRefresh,
  isExpanded,
  onToggle,
}: {
  dataset: Dataset;
  onRefresh: () => void;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const [configuring, setConfiguring] = useState(false);
  const [targetVariable, setTargetVariable] = useState(
    dataset.target_variable || ""
  );
  const [taskType, setTaskType] = useState<"classification" | "regression">(
    dataset.task_type || "classification"
  );
  const [trainingRuns, setTrainingRuns] = useState<TrainingRun[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(false);
  const [generatingPipeline, setGeneratingPipeline] = useState(false);

  useEffect(() => {
    if (isExpanded && dataset.id) {
      loadTrainingRuns();
    }
  }, [isExpanded, dataset.id]);

  const loadTrainingRuns = async () => {
    setLoadingRuns(true);
    try {
      const response = await datasetAPI.getTrainingRuns(dataset.id);
      setTrainingRuns(response.data.training_runs);
    } catch (error) {
      console.error("Error loading training runs:", error);
    } finally {
      setLoadingRuns(false);
    }
  };

  const handleConfigure = async () => {
    try {
      await datasetAPI.configure(dataset.id, targetVariable, taskType);
      onRefresh();
      setConfiguring(false);
    } catch (error) {
      console.error("Error configuring dataset:", error);
    }
  };

  const handleGeneratePipeline = async () => {
    setGeneratingPipeline(true);
    try {
      const response = await datasetAPI.generatePipeline(dataset.id);
      await loadTrainingRuns();
      
      // Automatically start training
      await trainingAPI.train(response.data.training_run.id);
      await loadTrainingRuns();
    } catch (error) {
      console.error("Error generating pipeline:", error);
      alert("Error: " + (error as any).response?.data?.error || "Pipeline generation failed");
    } finally {
      setGeneratingPipeline(false);
    }
  };

  const columns = Object.keys(dataset.columns_info || {});

  return (
    <div className="card">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={onToggle}
      >
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {dataset.filename}
          </h3>
          <p className="text-sm text-gray-600">
            Uploaded {new Date(dataset.uploaded_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          {dataset.target_variable && (
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
              Configured
            </span>
          )}
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${
              isExpanded ? "transform rotate-180" : ""
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </div>

      {isExpanded && (
        <div className="mt-6 space-y-6">
          {/* Column Info */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">
              Dataset Overview
            </h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-2">
                <strong>Columns:</strong> {columns.length}
              </p>
              <p className="text-sm text-gray-600 mb-2">
                <strong>Rows:</strong>{" "}
                {dataset.preprocessing_info?.final_shape?.[0] || "N/A"}
              </p>
              {dataset.preprocessing_info?.rows_removed > 0 && (
                <p className="text-sm text-gray-600">
                  <strong>Rows removed during preprocessing:</strong>{" "}
                  {dataset.preprocessing_info.rows_removed}
                </p>
              )}
            </div>
          </div>

          {/* Configuration */}
          {!dataset.target_variable ? (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">
                Configure Dataset
              </h4>
              {!configuring ? (
                <button
                  onClick={() => setConfiguring(true)}
                  className="btn btn-primary"
                >
                  Configure Target & Task Type
                </button>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="label">Target Variable</label>
                    <select
                      className="input"
                      value={targetVariable}
                      onChange={(e) => setTargetVariable(e.target.value)}
                    >
                      <option value="">Select target column</option>
                      {columns.map((col) => (
                        <option key={col} value={col}>
                          {col}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="label">Task Type</label>
                    <select
                      className="input"
                      value={taskType}
                      onChange={(e) =>
                        setTaskType(e.target.value as "classification" | "regression")
                      }
                    >
                      <option value="classification">Classification</option>
                      <option value="regression">Regression</option>
                    </select>
                  </div>

                  <div className="flex space-x-4">
                    <button
                      onClick={() => setConfiguring(false)}
                      className="btn btn-secondary"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleConfigure}
                      className="btn btn-primary"
                      disabled={!targetVariable}
                    >
                      Save Configuration
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">
                Configuration
              </h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Target Variable:</strong> {dataset.target_variable}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Task Type:</strong>{" "}
                  {dataset.task_type?.charAt(0).toUpperCase() +
                    dataset.task_type?.slice(1)}
                </p>
              </div>

              {trainingRuns.length === 0 && (
                <button
                  onClick={handleGeneratePipeline}
                  className="btn btn-primary mt-4"
                  disabled={generatingPipeline}
                >
                  {generatingPipeline
                    ? "Generating Pipeline & Training..."
                    : "Generate Pipeline & Train"}
                </button>
              )}
            </div>
          )}

          {/* Training Runs */}
          {trainingRuns.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">
                Training History
              </h4>
              <div className="space-y-4">
                {trainingRuns.map((run) => (
                  <TrainingRunCard key={run.id} run={run} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TrainingRunCard({ run }: { run: TrainingRun }) {
  const [expanded, setExpanded] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-700";
      case "running":
        return "bg-blue-100 text-blue-700";
      case "failed":
        return "bg-red-100 text-red-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div>
          <span
            className={`px-2 py-1 rounded-full text-xs ${getStatusColor(
              run.status
            )}`}
          >
            {run.status}
          </span>
          <p className="text-sm text-gray-600 mt-1">
            {new Date(run.created_at).toLocaleString()}
          </p>
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${
            expanded ? "transform rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>

      {expanded && run.status === "completed" && run.metrics && (
        <div className="mt-4 space-y-4">
          {/* Model Results */}
          <div>
            <h5 className="font-semibold text-gray-900 mb-2">
              Model Performance
            </h5>
            <div className="space-y-3">
              {Object.entries(run.metrics).map(([modelName, modelData]: any) => {
                if (modelData.error) {
                  return (
                    <div
                      key={modelName}
                      className="bg-red-50 border border-red-200 rounded p-3"
                    >
                      <p className="font-medium text-red-900">{modelName}</p>
                      <p className="text-sm text-red-700">
                        Error: {modelData.error}
                      </p>
                    </div>
                  );
                }

                return (
                  <div
                    key={modelName}
                    className="bg-gray-50 rounded p-3"
                  >
                    <p className="font-medium text-gray-900 mb-2">
                      {modelName}
                    </p>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(modelData.metrics).map(
                        ([metric, value]: any) => {
                          if (metric === "confusion_matrix") return null;
                          return (
                            <div key={metric} className="text-sm">
                              <span className="text-gray-600">
                                {metric.toUpperCase()}:
                              </span>
                              <span className="ml-2 font-medium">
                                {typeof value === "number"
                                  ? value.toFixed(4)
                                  : value}
                              </span>
                            </div>
                          );
                        }
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Data Story */}
          {run.result?.data_story && (
            <div>
              <h5 className="font-semibold text-gray-900 mb-2">
                AI-Generated Insights
              </h5>
              <div className="bg-gray-50 rounded-lg p-4 prose prose-sm max-w-none">
                <ReactMarkdown>{run.result.data_story}</ReactMarkdown>
              </div>
            </div>
          )}

          {/* Interpretation */}
          {run.result?.interpretation && (
            <div>
              <h5 className="font-semibold text-gray-900 mb-2">
                Results Interpretation
              </h5>
              <div className="bg-gray-50 rounded-lg p-4 prose prose-sm max-w-none">
                <ReactMarkdown>{run.result.interpretation}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}

      {expanded && run.status === "failed" && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded p-3">
          <p className="text-sm text-red-700">{run.error_message}</p>
        </div>
      )}
    </div>
  );
}

function FederatedTab({
  federatedStatus,
}: {
  federatedStatus: FederatedLearningStatus;
}) {
  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Federated Learning Overview
        </h2>
        <p className="text-gray-600 mb-4">
          This project has {federatedStatus.total_participants} participant(s)
          with their own datasets and training instances.
        </p>

        {federatedStatus.participants.length === 0 ? (
          <p className="text-gray-500">No participants yet</p>
        ) : (
          <div className="space-y-4">
            {federatedStatus.participants.map((participant, idx) => (
              <div
                key={idx}
                className="border border-gray-200 rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="font-medium text-gray-900">
                      {participant.user_email}
                    </p>
                    <p className="text-sm text-gray-600">
                      {participant.filename}
                    </p>
                  </div>
                  {participant.training_status && (
                    <span
                      className={`px-3 py-1 rounded-full text-sm ${
                        participant.training_status === "completed"
                          ? "bg-green-100 text-green-700"
                          : participant.training_status === "running"
                          ? "bg-blue-100 text-blue-700"
                          : participant.training_status === "failed"
                          ? "bg-red-100 text-red-700"
                          : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {participant.training_status}
                    </span>
                  )}
                </div>

                {participant.metrics && (
                  <div className="bg-gray-50 rounded p-3">
                    <p className="text-sm font-medium text-gray-900 mb-2">
                      Training Results
                    </p>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(participant.metrics).map(
                        ([modelName, modelData]: any) => {
                          if (modelData.error) return null;
                          const firstMetric = Object.entries(
                            modelData.metrics
                          )[0];
                          if (!firstMetric) return null;

                          return (
                            <div key={modelName} className="text-sm">
                              <span className="text-gray-600">
                                {modelName}:
                              </span>
                              <span className="ml-2 font-medium">
                                {firstMetric[0]}: {(firstMetric[1] as number).toFixed(4)}
                              </span>
                            </div>
                          );
                        }
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MembersTab({ members }: { members: any[] }) {
  return (
    <div className="card">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Project Members</h2>
      <div className="space-y-3">
        {members.map((member) => (
          <div
            key={member.user_id}
            className="flex items-center justify-between border-b border-gray-200 pb-3 last:border-0"
          >
            <div>
              <p className="font-medium text-gray-900">{member.email}</p>
              <p className="text-sm text-gray-600">
                Joined {new Date(member.joined_at).toLocaleDateString()}
              </p>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-sm ${
                member.role === "owner"
                  ? "bg-primary-100 text-primary-700"
                  : "bg-gray-100 text-gray-700"
              }`}
            >
              {member.role}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function UploadDatasetModal({
  projectId,
  onClose,
  onSuccess,
}: {
  projectId: number;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setError("");
    setUploading(true);

    try {
      await datasetAPI.upload(projectId, file);
      onSuccess();
    } catch (err: any) {
      setError(
        err.response?.data?.error || "Failed to upload dataset. Please try again."
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-md w-full p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Upload Dataset
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="label">Dataset File (CSV or Excel)</label>
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="input"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Upload a CSV or Excel file containing your dataset
            </p>
          </div>

          <div className="flex space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary flex-1"
              disabled={uploading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary flex-1"
              disabled={!file || uploading}
            >
              {uploading ? "Uploading..." : "Upload"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

