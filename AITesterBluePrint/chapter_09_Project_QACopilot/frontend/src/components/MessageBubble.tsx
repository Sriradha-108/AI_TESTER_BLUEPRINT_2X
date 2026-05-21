import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import type { Message } from "../api/types";
import SaveButton from "./SaveButton";

interface Props {
  message: Message;
  onCitationClick: (id: number) => void;
}

export default function MessageBubble({ message, onCitationClick }: Props) {
  const isUser = message.role === "user";

  // Replace [N] markers with clickable buttons after rendering
  const processedText = message.text;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-primary-500 text-white"
            : "bg-white border border-surface-200 text-surface-900"
        }`}
      >
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.text}</p>
        ) : (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || "");
                  const inline = !match;
                  if (inline) {
                    // Check if it's a citation like [1], [2]
                    const text = String(children).trim();
                    const citMatch = /^\[(\d+)\]$/.exec(text);
                    if (citMatch) {
                      const id = parseInt(citMatch[1]);
                      return (
                        <button
                          className="citation-chip"
                          onClick={() => onCitationClick(id)}
                          title={`View source ${id}`}
                        >
                          {id}
                        </button>
                      );
                    }
                    return (
                      <code className="bg-surface-100 px-1 py-0.5 rounded text-xs" {...props}>
                        {children}
                      </code>
                    );
                  }
                  return (
                    <SyntaxHighlighter
                      language={match[1]}
                      PreTag="div"
                      customStyle={{ fontSize: "0.75rem", borderRadius: "0.5rem" }}
                    >
                      {String(children).replace(/\n$/, "")}
                    </SyntaxHighlighter>
                  );
                },
                // Handle [N] in regular text
                p({ children, ...props }) {
                  return <p {...props}>{processCitations(children, onCitationClick)}</p>;
                },
                li({ children, ...props }) {
                  return <li {...props}>{processCitations(children, onCitationClick)}</li>;
                },
              }}
            >
              {processedText}
            </ReactMarkdown>
          </div>
        )}

        {/* Save button for saveable messages */}
        {message.saveable && (
          <SaveButton
            messageId={message.id}
            kind={message.saveable.kind}
            framework={message.saveable.framework}
            tcId={message.saveable.tc_id}
          />
        )}
      </div>
    </div>
  );
}

/**
 * Process text children to replace [N] patterns with citation chips.
 */
function processCitations(
  children: React.ReactNode,
  onClick: (id: number) => void
): React.ReactNode {
  if (!children) return children;

  if (typeof children === "string") {
    const parts = children.split(/(\[\d+\])/g);
    if (parts.length === 1) return children;

    return parts.map((part, i) => {
      const match = /^\[(\d+)\]$/.exec(part);
      if (match) {
        const id = parseInt(match[1]);
        return (
          <button
            key={i}
            className="citation-chip"
            onClick={() => onClick(id)}
            title={`View source ${id}`}
          >
            {id}
          </button>
        );
      }
      return part;
    });
  }

  if (Array.isArray(children)) {
    return children.map((child, i) => {
      if (typeof child === "string") {
        return <span key={i}>{processCitations(child, onClick)}</span>;
      }
      return child;
    });
  }

  return children;
}
