import { cookies } from "next/headers";
import Link from "next/link";
import { ReactNode } from "react";

import { AuthActions } from "@/components/layout/auth-actions";
import { AUTH_COOKIE_NAME } from "@/lib/auth";

const navigation = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/customers", label: "Customers" },
  { href: "/approvals", label: "Approvals" },
  { href: "/agent", label: "Agent" }
];

export function AppShell({ children }: { children: ReactNode }) {
  const hasToken = Boolean(cookies().get(AUTH_COOKIE_NAME)?.value);

  return (
    <div className="mx-auto min-h-screen max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="grid gap-6 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside className="panel flex min-h-[calc(100vh-3rem)] flex-col p-5">
          <div>
            <div className="mb-8">
              <p className="text-xs uppercase tracking-[0.3em] text-spruce">Agentic CRM</p>
              <h1 className="font-display text-3xl">Customer Master</h1>
            </div>
            <nav className="space-y-2">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="block rounded-2xl px-4 py-3 text-sm font-medium text-ink transition hover:bg-spruce hover:text-white"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
          <div className="mt-auto pt-6">
            <AuthActions initialHasToken={hasToken} />
          </div>
        </aside>
        <main>{children}</main>
      </div>
    </div>
  );
}
