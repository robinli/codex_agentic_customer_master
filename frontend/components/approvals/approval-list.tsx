import Link from "next/link";

import { ApprovalItem } from "@/lib/types";

export function ApprovalList({ items }: { items: ApprovalItem[] }) {
  return (
    <div className="grid gap-4">
      {items.map((item) => (
        <article key={item.id} className="panel p-5">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-spruce">{item.risk_level} risk</p>
              <h3 className="text-lg font-semibold">{item.action}</h3>
            </div>
            <span className="rounded-full bg-brass/15 px-3 py-1 text-xs font-semibold text-brass">{item.status}</span>
          </div>
          <p className="text-sm text-ink/70">{item.reason}</p>
          <Link href={`/approvals/${item.id}`} className="mt-3 inline-block text-sm font-semibold text-spruce hover:underline">
            View approval
          </Link>
          <p className="mt-3 text-xs text-ink/50">{new Date(item.created_at).toLocaleString()}</p>
        </article>
      ))}
    </div>
  );
}
