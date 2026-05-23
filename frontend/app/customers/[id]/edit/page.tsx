import { notFound } from "next/navigation";

import { CustomerForm } from "@/components/customers/customer-form";
import { AppShell } from "@/components/layout/app-shell";
import { fetchCustomerServer } from "@/lib/server-api";

export default async function CustomerEditPage({ params }: { params: { id: string } }) {
  const customer = await fetchCustomerServer(params.id).catch(() => null);
  if (!customer) {
    notFound();
  }

  return (
    <AppShell>
      <CustomerForm mode="edit" customer={customer} />
    </AppShell>
  );
}
