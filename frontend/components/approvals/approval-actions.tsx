"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { approveApproval, rejectApproval } from "@/lib/api";

export function ApprovalActions({ approvalId, status }: { approvalId: string; status: string }) {
  const router = useRouter();
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleApprove() {
    setSubmitting(true);
    setError(null);
    try {
      await approveApproval(approvalId);
      router.refresh();
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : "Approve failed");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleReject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await rejectApproval(approvalId, comment || "Rejected by approver");
      router.refresh();
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : "Reject failed");
    } finally {
      setSubmitting(false);
    }
  }

  if (status !== "pending") {
    return <p className="mt-6 text-sm text-ink/60">This approval is already {status}.</p>;
  }

  return (
    <div className="mt-6">
      <div className="mb-4 flex gap-3">
        <button
          type="button"
          className="rounded-2xl bg-spruce px-5 py-3 text-sm font-semibold text-white"
          onClick={handleApprove}
          disabled={submitting}
        >
          Approve
        </button>
      </div>
      <form onSubmit={handleReject} className="space-y-3">
        <textarea
          className="min-h-28 w-full rounded-2xl border border-black/10 bg-white px-4 py-3"
          placeholder="Reject comment"
          value={comment}
          onChange={(event) => setComment(event.target.value)}
        />
        <button className="rounded-2xl bg-brass px-5 py-3 text-sm font-semibold text-white" disabled={submitting}>
          Reject
        </button>
      </form>
      {error ? <p className="mt-3 text-sm text-red-700">{error}</p> : null}
    </div>
  );
}
