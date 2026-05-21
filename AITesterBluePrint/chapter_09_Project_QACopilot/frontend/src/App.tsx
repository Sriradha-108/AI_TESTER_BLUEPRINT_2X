import { useState, useCallback } from "react";
import type { Citation } from "./api/types";
import ChatPane from "./components/ChatPane";
import SourcePanel from "./components/SourcePanel";
import SourceFilter from "./components/SourceFilter";
import IngestStatus from "./components/IngestStatus";

function getSessionId(): string {
  const key = "qa_copilot_session";
  let id = sessionStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(key, id);
  }
  return id;
}

export default function App() {
  const [sessionId] = useState(getSessionId);
  const [forceCollections, setForceCollections] = useState<string[]>([]);
  const [framework, setFramework] = useState("auto");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [highlightId, setHighlightId] = useState<number | null>(null);

  const handleCitations = useCallback((newCitations: Citation[]) => {
    setCitations(newCitations);
    setHighlightId(null);
  }, []);

  const handleCitationClick = useCallback((id: number) => {
    setHighlightId(id);
  }, []);

  return (
    <div className="h-screen flex">
      {/* Left sidebar */}
      <aside className="w-56 border-r border-surface-200 bg-white p-3 flex flex-col gap-6 overflow-y-auto">
        <div className="flex items-center gap-2 pb-3 border-b border-surface-200">
          <div className="w-7 h-7 bg-primary-500 rounded-lg flex items-center justify-center">
            <span className="text-white text-xs font-bold">QA</span>
          </div>
          <span className="font-semibold text-sm">QA Copilot</span>
        </div>
        <SourceFilter
          forceCollections={forceCollections}
          onCollectionsChange={setForceCollections}
          framework={framework}
          onFrameworkChange={setFramework}
        />
        <IngestStatus />
      </aside>

      {/* Center chat */}
      <main className="flex-1 flex flex-col min-w-0">
        <ChatPane
          sessionId={sessionId}
          forceCollections={forceCollections}
          framework={framework}
          onCitations={handleCitations}
          onCitationClick={handleCitationClick}
        />
      </main>

      {/* Right source panel */}
      <aside className="w-80 border-l border-surface-200 bg-white overflow-hidden">
        <SourcePanel citations={citations} highlightId={highlightId} />
      </aside>
    </div>
  );
}
