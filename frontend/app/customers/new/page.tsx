import { CustomerForm } from "@/components/customers/customer-form";
import { AppShell } from "@/components/layout/app-shell";

export default function NewCustomerPage() {
  return (
    <AppShell>
      <CustomerForm mode="create" />
    </AppShell>
  );
}
