"use client";

import { useState, useRef, useEffect } from "react";
import { api } from "@/lib/api";
import { RiskChip } from "../components/ui/RiskChip";
import type { ChatMessage, ChatResponse } from "@/types/api";

const SUGGESTED_QUERIES = [
  "Why does Sarah not have Epic access?",
  "Compare John Smith's access to his expected baseline.",
  "Show me what baseline access Priya Patel should have.",
  "Which entitlements look excessive for David Kim?",
  "Recommend cleanup for Bob External.",
  "What changed after David Kim moved from Finance to IT?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const message = text || input;
    if (!message.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInput("");
    setLoading(true);

    try {
      const response: ChatResponse = await api.chat(message);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer, data: response },
      ]);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${e.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900">IAM Assistant</h1>
        <p className="text-sm text-gray-500 mt-1">Ask questions about identity and access management</p>
      </div>

      {/* Chat area */}
      <div className="flex-1 overflow-auto card p-4 mb-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-6">Try asking a question:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-2xl mx-auto">
              {SUGGESTED_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-left p-3 border rounded-lg hover:bg-gray-50 text-sm text-gray-700 transition-colors"
                >
                  &quot;{q}&quot;
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 text-sm ${
                msg.role === "user"
                  ? "bg-primary-600 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>

              {/* Evidence panel for assistant messages */}
              {msg.data && msg.data.evidence && msg.data.evidence.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs font-medium text-gray-500 mb-2">Evidence & Context</p>
                  <div className="flex gap-2 flex-wrap">
                    <span className="chip bg-blue-50 text-blue-700 text-xs">
                      Intent: {msg.data.intent}
                    </span>
                    {msg.data.risk_level && (
                      <RiskChip level={msg.data.risk_level} />
                    )}
                    {msg.data.requires_action && (
                      <span className="chip bg-orange-100 text-orange-800 text-xs">
                        Action Required
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {msg.data?.recommendations && (msg.data.recommendations as any[]).length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs font-medium text-gray-500 mb-1">Recommendations</p>
                  {(msg.data.recommendations as any[]).map((rec: any, j: number) => (
                    <div key={j} className="text-xs bg-white rounded p-2 mt-1 border">
                      <div className="flex items-center gap-1">
                        <RiskChip level={rec.risk_level} />
                        <span>{rec.title}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3 text-sm text-gray-500">
              Analyzing...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask an IAM question..."
          className="input flex-1"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()} className="btn-primary">
          Send
        </button>
      </form>
    </div>
  );
}
