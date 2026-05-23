import { UsersAdmin } from "@/components/settings/users-admin";
import { AppShell } from "@/components/layout/app-shell";
import { fetchSystemUsersServer } from "@/lib/server-api";

export default async function SettingsUsersPage() {
  const users = await fetchSystemUsersServer().catch(() => []);

  return (
    <AppShell>
      <UsersAdmin users={users} />
    </AppShell>
  );
}
