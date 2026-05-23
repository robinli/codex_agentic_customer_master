import Link from "next/link";

import { CustomerTable } from "@/components/customers/customer-table";
import { AppShell } from "@/components/layout/app-shell";
import { fetchCustomersServer } from "@/lib/server-api";

const fallbackItems = [
  {
    id: "demo-1",
    customer_code: "CUST001",
    customer_name: "大明有限公司",
    customer_type: "customer",
    status: "active",
    phone: "02-1234-5678",
    updated_at: new Date().toISOString()
  }
];

export default async function CustomersPage({
  searchParams
}: {
  searchParams?: { q?: string };
}) {
  const response = await fetchCustomersServer(searchParams?.q).catch(() => null);
  const items = response?.items ?? fallbackItems;

  return (
    <AppShell>
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-spruce">Customer Master</p>
          <h2 className="font-display text-4xl">Customers</h2>
        </div>
        <Link href="/customers/new" className="rounded-2xl bg-ink px-5 py-3 text-sm font-semibold text-white">
          New Customer
        </Link>
      </div>
      <form className="mb-5">
        <input
          name="q"
          defaultValue={searchParams?.q ?? ""}
          placeholder="Search by code, name, or tax id"
          className="w-full rounded-2xl border border-black/10 bg-white px-4 py-3 md:max-w-md"
        />
      </form>
      <CustomerTable items={items} />
    </AppShell>
  );
}
