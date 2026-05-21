import { useState } from "react";
import { Download, Check, AlertCircle } from "lucide-react";
import { saveMessage } from "../api/client";
import type { SaveRequest } from "../api/types";

interface Props {
  messageId: string;
  kind: "csv" | "code";
  framework?: string;
  tcId?: string;
}

export default function SaveButton({ messageId, kind, framework, tcId }: Props) {
  const [status, setStatus] = useState<"idle" | "saving" | "done" | "error" | "conflict">("idle");
  const [path, setPath] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSave = async (overwrite = false) => {
    setStatus("saving");
    const req: SaveRequest = {
      message_id: messageId,
      framework: framework,
      tc_id: tcId,
      overwrite,
    };

    try {
      const res = await saveMessage(req);
      setPath(res.written_path);
      setStatus("done");
    } catch (e: unknown) {
      const msg = String(e);
      if (msg.includes("already exists")) {
        setStatus("conflict");
        setErrorMsg(msg);
      } else {
        setStatus("error");
        setErrorMsg(msg);
      }
    }
  };

  if (status === "done") {
    return (
      <div className="flex items-center gap-1 text-xs text-green-700 mt-1">
        <Check size={12} />
        Saved to: {path}
      </div>
    );
  }

  if (status === "conflict") {
    return (
      <div className="mt-1 space-y-1">
        <p className="text-xs text-amber-700 flex items-center gap-1">
          <AlertCircle size={12} /> File exists. Overwrite?
        </p>
        <button
          onClick={() => handleSave(true)}
          className="text-xs px-2 py-1 bg-amber-500 text-white rounded hover:bg-amber-600"
        >
          Yes, overwrite
        </button>
      </div>
    );
  }

  if (status === "error") {
    return (
      <p className="text-xs text-red-600 mt-1 flex items-center gap-1">
        <AlertCircle size={12} /> {errorMsg}
      </p>
    );
  }

  return (
    <button
      onClick={() => handleSave(false)}
      disabled={status === "saving"}
      className="mt-1 flex items-center gap-1 text-xs px-2 py-1 bg-primary-500 text-white rounded hover:bg-primary-600 disabled:opacity-50"
    >
      <Download size={12} />
      {status === "saving" ? "Saving..." : `Save to disk (${kind})`}
    </button>
  );
}
