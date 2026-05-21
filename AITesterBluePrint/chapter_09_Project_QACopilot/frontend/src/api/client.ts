import type { ChatRequest, Citation, HealthResponse, SaveRequest, SaveResponse } from "./types";

interface ChatCallbacks {
  onSources: (sources: Citation[], messageId: string) => void;
  onToken: (text: string) => void;
  onDone: (messageId: string) => void;
  onError: (error: string) => void;
}

export async function chatStream(req: ChatRequest, callbacks: ChatCallbacks): Promise<void> {
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });

    if (!response.ok) {
      const err = await response.text();
      callbacks.onError(`HTTP ${response.status}: ${err}`);
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      callbacks.onError("No response body");
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Parse SSE events from buffer
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Keep incomplete line in buffer

      let eventType = "";
      for (const line of lines) {
        if (line.startsWith("event: ")) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          const data = line.slice(6);
          try {
            const parsed = JSON.parse(data);
            switch (eventType) {
              case "sources":
                callbacks.onSources(parsed.sources, parsed.message_id);
                break;
              case "token":
                callbacks.onToken(parsed.text);
                break;
              case "done":
                callbacks.onDone(parsed.message_id);
                break;
            }
          } catch {
            // Skip malformed JSON
          }
          eventType = "";
        }
      }
    }
  } catch (err) {
    callbacks.onError(String(err));
  }
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch("/api/health");
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function runIngest(source: string): Promise<{ status: string; detail: string }> {
  const res = await fetch(`/api/ingest/${source}`, { method: "POST" });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Ingest failed: ${err}`);
  }
  return res.json();
}

export async function saveMessage(req: SaveRequest): Promise<SaveResponse> {
  const res = await fetch("/api/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Save failed: ${res.status}`);
  }
  return res.json();
}
