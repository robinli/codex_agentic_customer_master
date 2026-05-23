import { ApprovalList } from "@/components/approvals/approval-list";
import { AppShell } from "@/components/layout/app-shell";
import { fetchApprovalsServer } from "@/lib/server-api";

const fallbackApprovals = [
  {
    id: "approval-1",
    target_type: "customer",
    target_id: "customer-1",
    action: "update",
    risk_level: "high",
    status: "pending",
    reason: "Change payment terms to net 60 days",
    created_at: new Date().toISOString()
  }
];

export default async function ApprovalsPage() {
  const approvals = await fetchApprovalsServer().catch(() => fallbackApprovals);

  return (
    <AppShell>
      <div className="mb-5">
        <p className="text-xs uppercase tracking-[0.25em] text-spruce">Workflow</p>
        <h2 className="font-display text-4xl">Approvals</h2>
      </div>
      <ApprovalList items={approvals} />
    </AppShell>
  );
}
