"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { createCustomer, updateCustomer } from "@/lib/api";
import { CustomerDetail } from "@/lib/types";

type CustomerFormProps = {
  mode: "create" | "edit";
  customer?: CustomerDetail;
};

type FormState = {
  customer_code: string;
  customer_name: string;
  customer_type: string;
  tax_id: string;
  status: string;
  phone: string;
  email: string;
  website: string;
  industry: string;
  payment_terms: string;
  credit_limit: string;
  note: string;
};

function toFormState(customer?: CustomerDetail): FormState {
  return {
    customer_code: customer?.customer_code ?? "",
    customer_name: customer?.customer_name ?? "",
    customer_type: customer?.customer_type ?? "customer",
    tax_id: customer?.tax_id ?? "",
    status: customer?.status ?? "active",
    phone: customer?.phone ?? "",
    email: customer?.email ?? "",
    website: customer?.website ?? "",
    industry: customer?.industry ?? "",
    payment_terms: customer?.payment_terms ?? "",
    credit_limit: customer?.credit_limit ? String(customer.credit_limit) : "",
    note: customer?.note ?? ""
  };
}

export function CustomerForm({ mode, customer }: CustomerFormProps) {
  const router = useRouter();
  const [form, setForm] = useState<FormState>(toFormState(customer));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultMessage, setResultMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setResultMessage(null);

    const payload = {
      ...form,
      tax_id: form.tax_id || undefined,
      phone: form.phone || undefined,
      email: form.email || undefined,
      website: form.website || undefined,
      industry: form.industry || undefined,
      payment_terms: form.payment_terms || undefined,
      credit_limit: form.credit_limit || undefined,
      note: form.note || undefined
    };

    try {
      if (mode === "create") {
        const created = await createCustomer(payload);
        router.push(`/customers/${created.id}`);
        router.refresh();
        return;
      }

      if (!customer) {
        throw new Error("Missing customer");
      }

      const changedFields = Object.fromEntries(
        Object.entries(payload).filter(([key, value]) => value !== (toFormState(customer) as Record<string, string>)[key])
      );
      const result = await updateCustomer(customer.id, changedFields);
      setResultMessage(result.message);
      if (result.status === "updated") {
        router.refresh();
      }
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Submit failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="panel max-w-4xl p-6">
      <p className="text-xs uppercase tracking-[0.25em] text-spruce">{mode === "create" ? "Create" : "Edit"}</p>
      <h2 className="font-display text-4xl">{mode === "create" ? "New Customer" : customer?.customer_name}</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {[
          ["customer_code", "Customer Code"],
          ["customer_name", "Customer Name"],
          ["tax_id", "Tax ID"],
          ["customer_type", "Customer Type"],
          ["status", "Status"],
          ["phone", "Phone"],
          ["email", "Email"],
          ["website", "Website"],
          ["industry", "Industry"],
          ["payment_terms", "Payment Terms"],
          ["credit_limit", "Credit Limit"],
          ["note", "Note"]
        ].map(([key, label]) => (
          <label key={key} className="text-sm">
            <span className="mb-2 block font-medium">{label}</span>
            <input
              value={form[key as keyof FormState]}
              onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              className="w-full rounded-2xl border border-black/10 bg-white px-4 py-3"
              disabled={submitting || (mode === "edit" && key === "customer_code")}
            />
          </label>
        ))}
      </div>
      {error ? <p className="mt-4 text-sm text-red-700">{error}</p> : null}
      {resultMessage ? <p className="mt-4 text-sm text-spruce">{resultMessage}</p> : null}
      <button className="mt-6 rounded-2xl bg-spruce px-5 py-3 text-sm font-semibold text-white" disabled={submitting}>
        {submitting ? "Submitting..." : mode === "create" ? "Create Customer" : "Save Changes"}
      </button>
    </form>
  );
}

