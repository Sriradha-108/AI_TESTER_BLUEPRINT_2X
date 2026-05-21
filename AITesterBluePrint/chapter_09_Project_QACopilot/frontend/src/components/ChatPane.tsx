import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { chatStream } from "../api/client";
import type { Citation, Message } from "../api/types";
import MessageBubble from "./MessageBubble";

interface Props {
  sessionId: string;
  forceCollections: string[];
  framework: string;
  onCitations: (citations: Citation[]) => void;
  onCitationClick: (id: number) => void;
}

export default function ChatPane({
  sessionId,
  forceCollections,
  framework,
  onCitations,
  onCitationClick,
}: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || streaming) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      text: input.trim(),
    };

    const assistantMsg: Message = {
      id: "",
      role: "assistant",
      text: "",
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setInput("");
    setStreaming(true);

    let fullText = "";
    let messageId = "";
    let citations: Citation[] = [];

    await chatStream(
      {
        session_id: sessionId,
        message: userMsg.text,
        force_collections: forceCollections.length > 0 ? forceCollections : null,
        framework: framework !== "auto" ? framework : null,
      },
      {
        onSources: (sources, msgId) => {
          messageId = msgId;
          citations = sources;
          onCitations(sources);
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              last.id = msgId;
              last.citations = sources;
            }
            return updated;
          });
        },
        onToken: (text) => {
          fullText += text;
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              last.text = fullText;
            }
            return updated;
          });
        },
        onDone: (msgId) => {
          // Detect if saveable
          const saveable = detectSaveable(fullText, framework);
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              last.id = msgId;
              last.saveable = saveable || undefined;
            }
            return updated;
          });
          setStreaming(false);
        },
        onError: (error) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              last.text = `Error: ${error}`;
            }
            return updated;
          });
          setStreaming(false);
        },
      }
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-surface-700">
            <div className="text-center">
              <h2 className="text-lg font-semibold mb-2">QA Copilot</h2>
              <p className="text-sm">Ask about test cases, code, bugs, or docs for app.vwo.com</p>
              <div className="mt-4 text-xs text-surface-700 space-y-1">
                <p>Try: "List High priority test cases for SQL injection"</p>
                <p>Try: "Generate Playwright code for TC_LOGIN_001"</p>
                <p>Try: "Create test cases from KAN-3"</p>
              </div>
            </div>
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} onCitationClick={onCitationClick} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-surface-200 p-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask QA Copilot..."
          disabled={streaming}
          className="flex-1 border border-surface-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={streaming || !input.trim()}
          className="px-3 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 flex items-center gap-1"
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}

function detectSaveable(
  text: string,
  framework: string
): { kind: "csv" | "code"; framework?: string; tc_id?: string } | null {
  // Check for code blocks
  if (text.includes("```java") || text.includes("```typescript") || text.includes("```ts")) {
    const tcMatch = text.match(/TC_\w+/);
    return {
      kind: "code",
      framework: text.includes("```java") ? "selenium" : "playwright",
      tc_id: tcMatch?.[0],
    };
  }

  // Check for generated test case rows
  if (text.match(/TC_\w+.*,.*,.*,/)) {
    return { kind: "csv" };
  }

  // Check for markdown table with TC_ entries
  if (text.includes("| TC_")) {
    return { kind: "csv" };
  }

  return null;
}
