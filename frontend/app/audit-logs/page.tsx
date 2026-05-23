import { AppShell } from "@/components/layout/app-shell";
import { fetchAuditLogsServer } from "@/lib/server-api";

export default async function AuditLogsPage() {
  const logs = await fetchAuditLogsServer().catch(() => []);

  return (
    <AppShell>
      <section className="panel p-6">
        <p className="text-xs uppercase tracking-[0.25em] text-spruce">Traceability</p>
        <h2 className="font-display text-4xl">Audit Logs</h2>
        <div className="mt-6 space-y-3 text-sm">
          {logs.length ? (
            logs.map((log) => (
              <div key={log.id} className="rounded-2xl bg-black/5 p-4">
                <p className="font-semibold">{log.action}</p>
                <p className="text-ink/70">
                  {log.actor_type} -> {log.target_type} ({log.target_id ?? "n/a"})
                </p>
                <p className="text-ink/50">{new Date(log.created_at).toLocaleString()}</p>
              </div>
            ))
          ) : (
            <div className="rounded-2xl bg-black/5 p-4">No audit logs available or access denied.</div>
          )}
        </div>
      </section>
    </AppShell>
  );
}
