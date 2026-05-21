export type SourceType =
  | "selenium_code"
  | "playwright_code"
  | "vwo_testcases"
  | "vwo_docs"
  | "vwo_bugs";

export interface Citation {
  id: number;
  source_type: SourceType;
  source_path: string;
  score: number;
  text: string;
  // Code sources
  repo?: string;
  symbol?: string;
  kind?: string;
  start_line?: number;
  end_line?: number;
  test_title?: string;
  // Test case sources
  tc_id?: string;
  tc_name?: string;
  priority?: string;
  // PDF sources
  doc_title?: string;
  page?: number;
  section?: string;
  // Bug sources
  jira_id?: string;
  summary?: string;
  status?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  citations?: Citation[];
  saveable?: {
    kind: "csv" | "code";
    framework?: string;
    tc_id?: string;
  };
}

export interface ChatRequest {
  session_id: string;
  message: string;
  force_collections?: string[] | null;
  framework?: string | null;
}

export interface HealthResponse {
  status: string;
  collections: Record<string, number>;
  groq_model: string;
  embed_model: string;
  rerank_model: string;
}

export interface SaveRequest {
  message_id: string;
  framework?: string;
  tc_id?: string;
  overwrite?: boolean;
}

export interface SaveResponse {
  written_path: string;
  rows_appended?: number;
}
