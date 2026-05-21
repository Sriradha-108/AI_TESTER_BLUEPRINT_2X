import { useState, forwardRef } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import type { Citation } from "../api/types";

interface Props {
  citation: Citation;
  highlighted?: boolean;
}

const SourceCard = forwardRef<HTMLDivElement, Props>(({ citation, highlighted }, ref) => {
  const [expanded, setExpanded] = useState(false);

  const header = getHeader(citation);
  const badgeColor = getBadgeColor(citation.source_type);

  return (
    <div
      ref={ref}
      className={`border border-surface-200 rounded-lg p-3 transition-all ${
        highlighted ? "source-card-highlight" : ""
      }`}
    >
      <div
        className="flex items-start gap-2 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <span className={`text-xs px-1.5 py-0.5 rounded font-mono ${badgeColor}`}>
          [{citation.id}]
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{header}</p>
          <p className="text-xs text-surface-700 truncate">
            {citation.source_type.replace("_", " ")}
          </p>
        </div>
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </div>

      {expanded && (
        <pre className="mt-2 text-xs bg-surface-100 rounded p-2 overflow-x-auto whitespace-pre-wrap max-h-60 overflow-y-auto">
          {citation.text}
        </pre>
      )}
    </div>
  );
});

SourceCard.displayName = "SourceCard";
export default SourceCard;

function getHeader(c: Citation): string {
  switch (c.source_type) {
    case "selenium_code":
    case "playwright_code":
      return `${c.repo || ""} · ${c.source_path}:${c.start_line}-${c.end_line} · ${c.symbol || ""}`;
    case "vwo_testcases":
      return `${c.tc_id} · ${c.tc_name} · ${c.priority}`;
    case "vwo_docs":
      return `${c.doc_title} · page ${c.page} · ${c.section || ""}`;
    case "vwo_bugs":
      return `${c.jira_id} · ${c.status} · ${c.priority} · ${c.summary || ""}`;
    default:
      return c.source_path;
  }
}

function getBadgeColor(type: string): string {
  switch (type) {
    case "selenium_code":
      return "bg-orange-100 text-orange-700";
    case "playwright_code":
      return "bg-green-100 text-green-700";
    case "vwo_testcases":
      return "bg-blue-100 text-blue-700";
    case "vwo_docs":
      return "bg-purple-100 text-purple-700";
    case "vwo_bugs":
      return "bg-red-100 text-red-700";
    default:
      return "bg-surface-100 text-surface-700";
  }
}
