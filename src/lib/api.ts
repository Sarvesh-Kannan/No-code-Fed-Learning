import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  code: string;
  description?: string;
  creator_id: number;
  created_at: string;
  member_count: number;
  role?: string;
  datasets?: Dataset[];
  members?: ProjectMember[];
}

export interface ProjectMember {
  user_id: number;
  email: string;
  role: string;
  joined_at: string;
}

export interface Dataset {
  id: number;
  project_id: number;
  user_id: number;
  filename: string;
  columns_info: Record<string, ColumnInfo>;
  preprocessing_info: PreprocessingInfo;
  target_variable?: string;
  task_type?: "classification" | "regression";
  uploaded_at: string;
}

export interface ColumnInfo {
  dtype: string;
  missing_count: number;
  missing_percentage: number;
  unique_count: number;
  mean?: number;
  std?: number;
  min?: number;
  max?: number;
  median?: number;
  top_values?: Record<string, number>;
}

export interface PreprocessingInfo {
  original_shape: [number, number];
  final_shape: [number, number];
  steps: Array<{
    step: string;
    column?: string;
    method?: string;
    missing_filled?: number;
    rows_removed?: number;
  }>;
  rows_removed: number;
}

export interface TrainingRun {
  id: number;
  dataset_id: number;
  pipeline: PipelineConfig;
  status: "pending" | "running" | "completed" | "failed";
  metrics?: Record<string, any>;
  error_message?: string;
  created_at: string;
  completed_at?: string;
  result?: ModelResult;
}

export interface PipelineConfig {
  preprocessing: {
    numeric_features: string[];
    categorical_features: string[];
    scaling_method: string;
    encoding_method: string;
  };
  feature_engineering: {
    polynomial_features: boolean;
    feature_selection: boolean;
    feature_selection_method: string;
  };
  models: Array<{
    name: string;
    type: string;
    hyperparameters: Record<string, any>;
    description: string;
  }>;
  validation: {
    method: string;
    test_size: number;
    cv_folds: number;
  };
  evaluation_metrics: string[];
}

export interface ModelResult {
  id: number;
  training_run_id: number;
  results_json: Record<string, any>;
  interpretation: string;
  data_story: string;
  visualizations?: any;
  created_at: string;
}

export interface FederatedLearningStatus {
  project_id: number;
  total_participants: number;
  participants: Array<{
    dataset_id: number;
    user_email: string;
    filename: string;
    uploaded_at: string;
    target_variable?: string;
    task_type?: string;
    training_status?: string;
    metrics?: Record<string, any>;
  }>;
}

// Auth APIs
export const authAPI = {
  signup: (email: string, password: string) =>
    api.post<{ token: string; user: User }>("/auth/signup", {
      email,
      password,
    }),

  login: (email: string, password: string) =>
    api.post<{ token: string; user: User }>("/auth/login", { email, password }),

  getCurrentUser: () => api.get<{ user: User }>("/auth/me"),
};

// Project APIs
export const projectAPI = {
  create: (name: string, description?: string) =>
    api.post<{ project: Project }>("/projects", { name, description }),

  join: (code: string) =>
    api.post<{ project: Project }>("/projects/join", { code }),

  list: () => api.get<{ projects: Project[] }>("/projects"),

  get: (projectId: number) =>
    api.get<{ project: Project }>(`/projects/${projectId}`),

  getFederatedStatus: (projectId: number) =>
    api.get<FederatedLearningStatus>(
      `/projects/${projectId}/federated-learning`
    ),
};

// Dataset APIs
export const datasetAPI = {
  upload: (projectId: number, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<{ dataset: Dataset }>(
      `/projects/${projectId}/datasets/upload`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
  },

  configure: (
    datasetId: number,
    targetVariable: string,
    taskType: "classification" | "regression"
  ) =>
    api.post<{ dataset: Dataset }>(`/datasets/${datasetId}/configure`, {
      target_variable: targetVariable,
      task_type: taskType,
    }),

  generatePipeline: (datasetId: number) =>
    api.post<{ training_run: TrainingRun }>(
      `/datasets/${datasetId}/generate-pipeline`
    ),

  getTrainingRuns: (datasetId: number) =>
    api.get<{ training_runs: TrainingRun[] }>(
      `/datasets/${datasetId}/training-runs`
    ),
};

// Training APIs
export const trainingAPI = {
  train: (trainingRunId: number) =>
    api.post<{ training_run: TrainingRun; results: ModelResult }>(
      `/training-runs/${trainingRunId}/train`
    ),
};

export default api;

