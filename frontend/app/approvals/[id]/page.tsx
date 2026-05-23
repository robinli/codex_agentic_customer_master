import Link from "next/link";
import { notFound } from "next/navigation";

import { ApprovalActions } from "@/components/approvals/approval-actions";
import { AppShell } from "@/components/layout/app-shell";
import { fetchApprovalServer } from "@/lib/server-api";

export default async function ApprovalDetailPage({ params }: { params: { id: string } }) {
  const approval = await fetchApprovalServer(params.id).catch(() => null);
  if (!approval) {
    notFound();
  }

  return (
    <AppShell>
      <section className="panel p-6">
        <p className="text-xs uppercase tracking-[0.25em] text-spruce">Approval Detail</p>
        <h2 className="font-display text-4xl">Approval {approval.id}</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl bg-black/5 p-4">
            <p className="text-sm font-medium">Before</p>
            <pre className="mt-2 whitespace-pre-wrap text-sm text-ink/70">
              {JSON.stringify(approval.before_data ?? {}, null, 2)}
            </pre>
          </div>
          <div className="rounded-2xl bg-black/5 p-4">
            <p className="text-sm font-medium">After</p>
            <pre className="mt-2 whitespace-pre-wrap text-sm text-ink/70">
              {JSON.stringify(approval.after_data ?? {}, null, 2)}
            </pre>
          </div>
        </div>
        <div className="mt-6 space-y-2 text-sm text-ink/70">
          <p>Action: {approval.action}</p>
          <p>Risk: {approval.risk_level}</p>
          <p>Status: {approval.status}</p>
          <p>Reason: {approval.reason}</p>
        </div>
        <ApprovalActions approvalId={approval.id} status={approval.status} />
        <Link href="/approvals" className="mt-6 inline-block rounded-2xl bg-ink px-5 py-3 text-sm font-semibold text-white">
          Back to approvals
        </Link>
      </section>
    </AppShell>
  );
}
