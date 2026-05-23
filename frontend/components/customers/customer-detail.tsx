import Link from "next/link";

import { CustomerDetail } from "@/lib/types";

export function CustomerDetailCard({ customer }: { customer: CustomerDetail }) {
  return (
    <div className="grid gap-6">
      <section className="panel p-6">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-spruce">Customer Detail</p>
            <h2 className="font-display text-4xl">{customer.customer_name}</h2>
          </div>
          <Link href={`/customers/${customer.id}/edit`} className="rounded-2xl bg-ink px-5 py-3 text-sm font-semibold text-white">
            Edit
          </Link>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl bg-black/5 p-4">Code: {customer.customer_code}</div>
          <div className="rounded-2xl bg-black/5 p-4">Status: {customer.status}</div>
          <div className="rounded-2xl bg-black/5 p-4">Tax ID: {customer.tax_id ?? "-"}</div>
          <div className="rounded-2xl bg-black/5 p-4">Type: {customer.customer_type}</div>
          <div className="rounded-2xl bg-black/5 p-4">Phone: {customer.phone ?? "-"}</div>
          <div className="rounded-2xl bg-black/5 p-4">Email: {customer.email ?? "-"}</div>
          <div className="rounded-2xl bg-black/5 p-4">Payment Terms: {customer.payment_terms ?? "-"}</div>
          <div className="rounded-2xl bg-black/5 p-4">Credit Limit: {customer.credit_limit ?? "-"}</div>
        </div>
      </section>
      <section className="panel p-6">
        <h3 className="text-xl font-semibold">Contacts</h3>
        <div className="mt-4 space-y-3">
          {customer.contacts.length ? (
            customer.contacts.map((contact) => (
              <div key={contact.id} className="rounded-2xl bg-black/5 p-4">
                {contact.name} {contact.phone ? `- ${contact.phone}` : ""}
              </div>
            ))
          ) : (
            <p className="text-sm text-ink/60">No contacts yet.</p>
          )}
        </div>
      </section>
      <section className="panel p-6">
        <h3 className="text-xl font-semibold">Addresses</h3>
        <div className="mt-4 space-y-3">
          {customer.addresses.length ? (
            customer.addresses.map((address) => (
              <div key={address.id} className="rounded-2xl bg-black/5 p-4">
                {address.address_type}: {address.city ?? ""} {address.district ?? ""} {address.address_line}
              </div>
            ))
          ) : (
            <p className="text-sm text-ink/60">No addresses yet.</p>
          )}
        </div>
      </section>
    </div>
  );
}
