import { useRef, useCallback, useEffect, useState } from "react";
import type { Citation } from "../api/types";
import SourceCard from "./SourceCard";

interface Props {
  citations: Citation[];
  highlightId: number | null;
}

export default function SourcePanel({ citations, highlightId }: Props) {
  const cardRefs = useRef<Map<number, HTMLDivElement>>(new Map());
  const [flashId, setFlashId] = useState<number | null>(null);

  const setRef = useCallback((id: number) => (el: HTMLDivElement | null) => {
    if (el) cardRefs.current.set(id, el);
    else cardRefs.current.delete(id);
  }, []);

  useEffect(() => {
    if (highlightId !== null) {
      const el = cardRefs.current.get(highlightId);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        setFlashId(highlightId);
        const timer = setTimeout(() => setFlashId(null), 800);
        return () => clearTimeout(timer);
      }
    }
  }, [highlightId]);

  if (!citations.length) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-surface-700">
        Sources will appear here
      </div>
    );
  }

  return (
    <div className="space-y-2 overflow-y-auto h-full p-2">
      <h3 className="text-xs font-semibold uppercase text-surface-700 sticky top-0 bg-white py-1">
        Sources ({citations.length})
      </h3>
      {citations.map((c) => (
        <SourceCard
          key={c.id}
          ref={setRef(c.id)}
          citation={c}
          highlighted={flashId === c.id}
        />
      ))}
    </div>
  );
}
