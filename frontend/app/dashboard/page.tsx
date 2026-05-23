import { AppShell } from "@/components/layout/app-shell";

export default function DashboardPage() {
  return (
    <AppShell>
      <section className="grid gap-6 md:grid-cols-3">
        <article className="panel p-6">
          <p className="text-xs uppercase tracking-[0.25em] text-spruce">Customers</p>
          <h2 className="mt-3 text-4xl font-display">128</h2>
          <p className="mt-2 text-sm text-ink/70">Active master records under maintenance.</p>
        </article>
        <article className="panel p-6">
          <p className="text-xs uppercase tracking-[0.25em] text-spruce">Pending Approvals</p>
          <h2 className="mt-3 text-4xl font-display">6</h2>
          <p className="mt-2 text-sm text-ink/70">Sensitive changes awaiting approver action.</p>
        </article>
        <article className="panel p-6">
          <p className="text-xs uppercase tracking-[0.25em] text-spruce">Agent Sessions</p>
          <h2 className="mt-3 text-4xl font-display">14</h2>
          <p className="mt-2 text-sm text-ink/70">Tracked conversations with tool call logging.</p>
        </article>
      </section>
    </AppShell>
  );
}

