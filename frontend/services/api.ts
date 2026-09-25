import {
  Repository,
  RepoListResponse,
  HealthCheckResponse,
  RepoFile,
  FileContentResponse,
  CodeChunk,
  IngestionSummary,
  ChatMessage,
  ChatSession,
  SendChatRequest,
  RepoIssue,
  CodeReviewResponse,
  PrGenerateResponse,
  SecurityFinding,
  SecurityScanSummaryResponse,
  QualityFinding,
  ArchitectureGraphResponse,
  TechDocsResponse
} from "@/types/repo";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred.";
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorJson.message || errorDetail;
    } catch {
      // Ignore json parse error
    }
    throw new ApiError(errorDetail, response.status);
  }

  return response.json();
}

export const api = {
  async healthCheck(): Promise<HealthCheckResponse> {
    return fetchJson<HealthCheckResponse>(`${API_BASE_URL}/api/v1/health`);
  },

  async analyzeRepo(githubUrl: string): Promise<Repository> {
    return fetchJson<Repository>(`${API_BASE_URL}/api/v1/repos/analyze`, {
      method: "POST",
      body: JSON.stringify({ github_url: githubUrl }),
    });
  },

  async getRepo(id: string): Promise<Repository> {
    return fetchJson<Repository>(`${API_BASE_URL}/api/v1/repos/${id}`);
  },

  async listRepos(): Promise<RepoListResponse> {
    return fetchJson<RepoListResponse>(`${API_BASE_URL}/api/v1/repos/`);
  },

  // Phase 2 Ingestion & File Methods
  async ingestRepo(repoId: string): Promise<IngestionSummary> {
    return fetchJson<IngestionSummary>(`${API_BASE_URL}/api/v1/repos/${repoId}/ingest`, {
      method: "POST",
    });
  },

  async getRepoFiles(repoId: string): Promise<RepoFile[]> {
    return fetchJson<RepoFile[]>(`${API_BASE_URL}/api/v1/repos/${repoId}/files`);
  },

  async getFileContent(repoId: string, path: string): Promise<FileContentResponse> {
    const encodedPath = encodeURIComponent(path);
    return fetchJson<FileContentResponse>(`${API_BASE_URL}/api/v1/repos/${repoId}/files/content?path=${encodedPath}`);
  },

  async getRepoChunks(repoId: string, path?: string): Promise<CodeChunk[]> {
    const query = path ? `?file_path=${encodeURIComponent(path)}` : "";
    return fetchJson<CodeChunk[]>(`${API_BASE_URL}/api/v1/repos/${repoId}/chunks${query}`);
  },

  // Phase 3 Chat Methods
  async sendChatMessage(repoId: string, payload: SendChatRequest): Promise<ChatMessage> {
    return fetchJson<ChatMessage>(`${API_BASE_URL}/api/v1/repos/${repoId}/chat`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getChatSessions(repoId: string): Promise<ChatSession[]> {
    return fetchJson<ChatSession[]>(`${API_BASE_URL}/api/v1/repos/${repoId}/chat/sessions`);
  },

  async getChatMessages(repoId: string, sessionId: string): Promise<ChatMessage[]> {
    return fetchJson<ChatMessage[]>(`${API_BASE_URL}/api/v1/repos/${repoId}/chat/messages?session_id=${sessionId}`);
  },

  // Phase 4 Issues Methods
  async syncRepoIssues(repoId: string): Promise<RepoIssue[]> {
    return fetchJson<RepoIssue[]>(`${API_BASE_URL}/api/v1/repos/${repoId}/issues/sync`, {
      method: "POST",
    });
  },

  async getRepoIssues(repoId: string, difficulty?: string): Promise<RepoIssue[]> {
    const query = difficulty ? `?difficulty=${encodeURIComponent(difficulty)}` : "";
    return fetchJson<RepoIssue[]>(`${API_BASE_URL}/api/v1/repos/${repoId}/issues${query}`);
  },

  async getRepoIssueDetail(repoId: string, issueNumber: number): Promise<RepoIssue> {
    return fetchJson<RepoIssue>(`${API_BASE_URL}/api/v1/repos/${repoId}/issues/${issueNumber}`);
  },

  // Phase 5 Contribute & Code Review Methods
  async reviewCodeDiff(repoId: string, gitDiff: string, issueNumber?: number): Promise<CodeReviewResponse> {
    return fetchJson<CodeReviewResponse>(`${API_BASE_URL}/api/v1/repos/${repoId}/review`, {
      method: "POST",
      body: JSON.stringify({ git_diff: gitDiff, issue_number: issueNumber }),
    });
  },

  async generatePrDescription(repoId: string, gitDiff: string, issueNumber?: number, testResults?: string): Promise<PrGenerateResponse> {
    return fetchJson<PrGenerateResponse>(`${API_BASE_URL}/api/v1/repos/${repoId}/generate-pr`, {
      method: "POST",
      body: JSON.stringify({ git_diff: gitDiff, issue_number: issueNumber, test_results: testResults }),
    });
  },

  // Phase 6 Security Methods
  async runSecurityScan(repoId: string): Promise<SecurityScanSummaryResponse> {
    return fetchJson<SecurityScanSummaryResponse>(`${API_BASE_URL}/api/v1/repos/${repoId}/security/scan`, {
      method: "POST",
    });
  },

  async getSecurityFindings(repoId: string, severity?: string): Promise<SecurityFinding[]> {
    const query = severity ? `?severity=${encodeURIComponent(severity)}` : "";
    return fetchJson<SecurityFinding[]>(`${API_BASE_URL}/api/v1/repos/${repoId}/security${query}`);
  },

  async getQualityFindings(repoId: string): Promise<QualityFinding[]> {
    return fetchJson<QualityFinding[]>(`${API_BASE_URL}/api/v1/repos/${repoId}/quality`);
  },

  // Phase 7 Architecture Methods
  async getArchitectureGraph(repoId: string): Promise<ArchitectureGraphResponse> {
    return fetchJson<ArchitectureGraphResponse>(`${API_BASE_URL}/api/v1/repos/${repoId}/architecture`);
  },

  async generateArchitectureGraph(repoId: string): Promise<ArchitectureGraphResponse> {
    return fetchJson<ArchitectureGraphResponse>(`${API_BASE_URL}/api/v1/repos/${repoId}/architecture/generate`, {
      method: "POST",
    });
  },

  // Phase 8 Documentation Methods
  async generateTechnicalDocs(repoId: string): Promise<TechDocsResponse> {
    return fetchJson<TechDocsResponse>(`${API_BASE_URL}/api/v1/repos/${repoId}/docs/generate`, {
      method: "POST",
    });
  },

  async getTechnicalDocs(repoId: string): Promise<TechDocsResponse> {
    return fetchJson<TechDocsResponse>(`${API_BASE_URL}/api/v1/repos/${repoId}/docs`);
  },
};
