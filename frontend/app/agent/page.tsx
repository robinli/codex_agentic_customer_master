import { AgentWorkspace } from "@/components/agent/agent-workspace";
import { AppShell } from "@/components/layout/app-shell";

export default function AgentPage() {
  return (
    <AppShell>
      <div className="mb-5">
        <p className="text-xs uppercase tracking-[0.25em] text-spruce">Natural Language Operations</p>
        <h2 className="font-display text-4xl">Agent Chat</h2>
      </div>
      <AgentWorkspace />
    </AppShell>
  );
}

