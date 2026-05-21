import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { getHealth, runIngest } from "../api/client";

export default function IngestStatus() {
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchCounts = async () => {
    try {
      const data = await getHealth();
      setCounts(data.collections);
      setError(null);
    } catch (e) {
      setError("Backend offline");
    }
  };

  useEffect(() => {
    fetchCounts();
  }, []);

  const handleIngest = async (source: string) => {
    setLoading(source);
    setError(null);
    try {
      await runIngest(source);
      await fetchCounts();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(null);
    }
  };

  return (
    <div>
      <h3 className="text-xs font-semibold uppercase text-surface-700 mb-2">
        Collections
      </h3>
      {error && (
        <p className="text-xs text-red-600 mb-2">{error}</p>
      )}
      <div className="space-y-1 text-sm">
        {Object.entries(counts).map(([name, count]) => (
          <div key={name} className="flex items-center justify-between px-2 py-1">
            <span className="truncate text-xs">{name}</span>
            <div className="flex items-center gap-1">
              <span className="text-xs font-mono text-surface-700">{count}</span>
              <button
                onClick={() => handleIngest(name.replace("vwo_", "").replace("_code", "")
                  .replace("selenium", "selenium")
                  .replace("playwright", "playwright")
                  .replace("testcases", "testcases")
                  .replace("docs", "pdfs")
                  .replace("bugs", "jira")
                )}
                disabled={loading !== null}
                className="p-0.5 rounded hover:bg-surface-200 disabled:opacity-50"
                title={`Re-ingest ${name}`}
              >
                <RefreshCw size={12} className={loading === name ? "animate-spin" : ""} />
              </button>
            </div>
          </div>
        ))}
      </div>
      <button
        onClick={() => handleIngest("all")}
        disabled={loading !== null}
        className="mt-2 w-full text-xs px-2 py-1.5 bg-primary-500 text-white rounded hover:bg-primary-600 disabled:opacity-50 flex items-center justify-center gap-1"
      >
        <RefreshCw size={12} className={loading === "all" ? "animate-spin" : ""} />
        Re-ingest All
      </button>
    </div>
  );
}
