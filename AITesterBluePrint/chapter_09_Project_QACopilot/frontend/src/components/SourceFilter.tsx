import { Database, Code, FileText, Bug, FlaskConical } from "lucide-react";

const COLLECTIONS = [
  { id: "selenium_code", label: "Selenium Code", icon: Code },
  { id: "playwright_code", label: "Playwright Code", icon: FlaskConical },
  { id: "vwo_testcases", label: "Test Cases", icon: Database },
  { id: "vwo_docs", label: "VWO Docs (PDF)", icon: FileText },
  { id: "vwo_bugs", label: "JIRA Bugs", icon: Bug },
] as const;

const FRAMEWORKS = ["auto", "selenium", "playwright"] as const;

interface Props {
  forceCollections: string[];
  onCollectionsChange: (collections: string[]) => void;
  framework: string;
  onFrameworkChange: (fw: string) => void;
}

export default function SourceFilter({
  forceCollections,
  onCollectionsChange,
  framework,
  onFrameworkChange,
}: Props) {
  const toggle = (id: string) => {
    if (forceCollections.includes(id)) {
      onCollectionsChange(forceCollections.filter((c) => c !== id));
    } else {
      onCollectionsChange([...forceCollections, id]);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-xs font-semibold uppercase text-surface-700 mb-2">
          Source Filter
        </h3>
        <p className="text-xs text-surface-700 mb-2">
          Check to override router (empty = auto)
        </p>
        <div className="space-y-1">
          {COLLECTIONS.map(({ id, label, icon: Icon }) => (
            <label
              key={id}
              className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-surface-100 cursor-pointer text-sm"
            >
              <input
                type="checkbox"
                checked={forceCollections.includes(id)}
                onChange={() => toggle(id)}
                className="rounded border-surface-300"
              />
              <Icon size={14} className="text-surface-700" />
              <span>{label}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-xs font-semibold uppercase text-surface-700 mb-2">
          Framework
        </h3>
        <select
          value={framework}
          onChange={(e) => onFrameworkChange(e.target.value)}
          className="w-full text-sm border border-surface-300 rounded px-2 py-1.5 bg-white"
        >
          {FRAMEWORKS.map((fw) => (
            <option key={fw} value={fw}>
              {fw.charAt(0).toUpperCase() + fw.slice(1)}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
