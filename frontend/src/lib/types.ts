export type JobStatus = "PENDING" | "IN_PROGRESS" | "COMPLETED" | "FAILED";

export type Stage =
  | "queued"
  | "scanning"
  | "extracting_functions"
  | "finding_edge_cases"
  | "generating_tests"
  | "running_tests"
  | "computing_coverage"
  | "completed";

export interface FunctionInfo {
  name: string;
  file?: string;
}

export interface EdgeCase {
  type: string;
  description: string;
  argument?: string;
  priority?: number;
}

export interface GeneratedTest {
  target_function: string;
  test_type: string;
  content: string;
  language?: string;
}

export interface TestResult {
  file: string;
  status: string;
  output?: string;
}

export interface Coverage {
  total_coverage: number;
  covered_lines: number;
  total_lines: number;
  executed?: boolean;
}

export interface Stats {
  files_scanned: number;
  total_loc: number;
  functions_found: number;
  functions_analyzed: number;
  test_modules: number;
  test_cases: number;
}

export interface AnalysisResult {
  job_id: string;
  status: JobStatus;
  stage?: Stage;
  error?: string;
  source_type?: string;
  created_at?: string;
  updated_at?: string;
  structure?: {
    languages?: Record<string, number>;
    functions?: FunctionInfo[];
  };
  stats?: Stats;
  edge_cases?: EdgeCase[];
  tests?: GeneratedTest[];
  test_results?: TestResult[];
  coverage?: Coverage;
}

export interface StartResponse {
  job_id: string;
  status: string;
  created_at: string;
}

export interface RecentJob {
  job_id: string;
  status: JobStatus;
  source_type?: string;
  created_at?: string;
  stats?: Stats | null;
}
