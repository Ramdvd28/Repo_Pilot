export interface Repository {
  id: string;
  github_url: string;
  owner: string;
  name: string;
  description?: string;
  stars: number;
  forks: number;
  open_issues: number;
  default_branch: string;
  primary_language?: string;
  languages: Record<string, number>;
  topics: string[];
  created_at: string;
  updated_at: string;
  analyzed_at?: string;
}

export interface RepoAnalyzeRequest {
  github_url: string;
}

export interface RepoListResponse {
  total: number;
  repositories: Repository[];
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  database: string;
  version: string;
}

export interface RepoFile {
  id: string;
  file_path: string;
  language?: string;
  size_bytes: number;
  total_lines: number;
}

export interface FileContentResponse {
  repository_id: string;
  file_path: string;
  language: string;
  content: string;
}

export interface CodeChunk {
  id: string;
  file_path: string;
  language?: string;
  start_line: number;
  end_line: number;
  symbol_name?: string;
  content: string;
}

export interface IngestionSummary {
  repository_id: string;
  status: string;
  files_indexed: number;
  chunks_created: number;
  languages_found: Record<string, number>;
  ingestion_time_seconds: number;
}

export interface ChunkSource {
  file_path: string;
  start_line: number;
  end_line: number;
  language?: string;
  symbol_name?: string;
  snippet?: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChunkSource[];
  created_at: string;
}

export interface ChatSession {
  id: string;
  repository_id: string;
  title: string;
  created_at: string;
}

export interface SendChatRequest {
  question: string;
  session_id?: string;
  provider?: string;
}

export interface RepoIssue {
  id: string;
  repository_id: string;
  issue_number: number;
  title: string;
  description?: string;
  difficulty_level: "beginner" | "intermediate" | "advanced";
  relevant_files: string[];
  suggested_approach?: string;
  created_at: string;
}

export interface CodeReviewFinding {
  severity: "error" | "warning" | "info";
  file_path: string;
  line_number?: number;
  explanation: string;
  suggested_fix?: string;
}

export interface CodeReviewResponse {
  score: number;
  summary: string;
  findings: CodeReviewFinding[];
}

export interface PrGenerateResponse {
  title: string;
  markdown_description: string;
}

// Phase 6 Security & Quality Types
export interface SecurityFinding {
  id?: string;
  rule_id: string;
  tool_name: string;
  severity: "critical" | "high" | "medium" | "low";
  file_path: string;
  line_number?: number;
  description: string;
  ai_explanation?: string;
}

export interface SecurityScanSummaryResponse {
  repository_id: string;
  total_findings: number;
  counts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  findings: SecurityFinding[];
}

export interface QualityFinding {
  id: string;
  tool_name: string;
  category: string;
  file_path: string;
  line_number?: number;
  message: string;
  ai_suggestion?: string;
}

// Phase 7 Architecture Graph Types
export interface ArchNodeData {
  label: string;
  category: "core" | "frontend" | "backend" | "database" | "ai" | "external" | "module";
  description: string;
  icon?: string;
}

export interface ArchNode {
  id: string;
  type: string;
  data: ArchNodeData;
  position: { x: number; y: number };
}

export interface ArchEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

export interface ArchitectureGraphResponse {
  repository_name: string;
  total_nodes: number;
  total_edges: number;
  nodes: ArchNode[];
  edges: ArchEdge[];
}

// Phase 8 Technical Documentation Types
export interface DocSection {
  id: string;
  title: string;
}

export interface TechDocsResponse {
  repository_id: string;
  owner: string;
  name: string;
  documentation: string;
  sections: DocSection[];
}
