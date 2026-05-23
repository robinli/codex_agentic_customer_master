import { notFound } from "next/navigation";

import { CustomerDetailCard } from "@/components/customers/customer-detail";
import { AppShell } from "@/components/layout/app-shell";
import { fetchCustomerServer } from "@/lib/server-api";

export default async function CustomerDetailPage({ params }: { params: { id: string } }) {
  const customer = await fetchCustomerServer(params.id).catch(() => null);
  if (!customer) {
    notFound();
  }

  return (
    <AppShell>
      <CustomerDetailCard customer={customer} />
    </AppShell>
  );
}
