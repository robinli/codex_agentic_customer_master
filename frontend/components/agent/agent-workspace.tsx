"use client";

import { useEffect, useState } from "react";

import { createAgentSession, fetchAgentMessages, fetchAgentSessions, sendAgentMessage } from "@/lib/api";
import { AgentMessage, AgentSession, AgentToolCall } from "@/lib/types";

export function AgentWorkspace() {
  const [sessions, setSessions] = useState<AgentSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [input, setInput] = useState("幫我查詢統編 12345678 的客戶");
  const [toolCalls, setToolCalls] = useState<AgentToolCall[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadSessions() {
    const list = await fetchAgentSessions();
    setSessions(list);
    if (!activeSessionId && list.length > 0) {
      setActiveSessionId(list[0].id);
    }
    return list;
  }

  async function loadMessages(sessionId: string) {
    const list = await fetchAgentMessages(sessionId);
    setMessages(list);
  }

  useEffect(() => {
    void loadSessions().catch((loadError) => {
      setError(loadError instanceof Error ? loadError.message : "Failed to load sessions");
    });
  }, []);

  useEffect(() => {
    if (!activeSessionId) {
      return;
    }
    void loadMessages(activeSessionId).catch((loadError) => {
      setError(loadError instanceof Error ? loadError.message : "Failed to load messages");
    });
  }, [activeSessionId]);

  async function handleCreateSession() {
    setError(null);
    try {
      const session = await createAgentSession("New session");
      const nextSessions = await loadSessions();
      setActiveSessionId(session.id);
      setSessions(nextSessions);
      setMessages([]);
      setToolCalls([]);
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Failed to create session");
    }
  }

  async function handleSendMessage() {
    if (!activeSessionId || !input.trim()) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await sendAgentMessage(activeSessionId, input);
      await loadMessages(activeSessionId);
      setToolCalls(response.tool_calls);
      setInput("");
      await loadSessions();
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : "Failed to send message");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
      <section className="panel p-5">
        <div className="mb-4 flex items-center justify-between">
          <p className="text-xs uppercase tracking-[0.25em] text-spruce">Sessions</p>
          <button className="rounded-2xl bg-ink px-3 py-2 text-xs font-semibold text-white" onClick={handleCreateSession}>
            New
          </button>
        </div>
        <div className="space-y-3">
          {sessions.length ? (
            sessions.map((session) => (
              <button
                key={session.id}
                className={`w-full rounded-2xl px-4 py-3 text-left text-sm font-medium ${
                  activeSessionId === session.id ? "bg-ink text-white" : "bg-black/5"
                }`}
                onClick={() => setActiveSessionId(session.id)}
              >
                {session.title || "Untitled session"}
              </button>
            ))
          ) : (
            <p className="text-sm text-ink/60">No sessions yet.</p>
          )}
        </div>
      </section>
      <section className="space-y-4">
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-spruce">Chat</p>
          <div className="mt-4 space-y-4">
            {messages.length ? (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={
                    message.role === "user"
                      ? "ml-auto max-w-xl rounded-3xl bg-ink p-4 text-white"
                      : message.role === "assistant"
                        ? "max-w-xl rounded-3xl bg-black/5 p-4"
                        : "max-w-xl rounded-3xl border border-dashed border-black/10 bg-white p-4"
                  }
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  {message.tool_name ? <p className="mt-2 text-xs uppercase tracking-[0.25em] text-brass">{message.tool_name}</p> : null}
                </div>
              ))
            ) : (
              <p className="text-sm text-ink/60">Start a session and send a message.</p>
            )}
          </div>
        </div>
        <div className="panel p-4">
          <div className="flex gap-3">
            <input
              className="flex-1 rounded-2xl border border-black/10 bg-white px-4 py-3 outline-none"
              placeholder="輸入自然語言，例如：把大明有限公司電話改成 02-1234-5678"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              disabled={!activeSessionId || loading}
            />
            <button
              className="rounded-2xl bg-spruce px-5 py-3 text-sm font-semibold text-white"
              onClick={handleSendMessage}
              disabled={!activeSessionId || loading}
            >
              {loading ? "Sending..." : "送出"}
            </button>
          </div>
          {error ? <p className="mt-3 text-sm text-red-700">{error}</p> : null}
        </div>
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-spruce">Tool Calls</p>
          <div className="mt-4 space-y-3">
            {toolCalls.length ? (
              toolCalls.map((call, index) => (
                <div key={`${call.tool_name}-${index}`} className="rounded-2xl bg-black/5 p-4 text-sm">
                  <p className="font-semibold">{call.tool_name}</p>
                  <p className="text-ink/60">Status: {call.status}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-ink/60">Tool activity will appear here.</p>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
