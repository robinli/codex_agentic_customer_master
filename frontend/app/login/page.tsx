"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { login } from "@/lib/api";
import { setBrowserAccessToken } from "@/lib/auth";

const demoAccounts = [
  { email: "admin@example.com", password: "admin1234", role: "admin" },
  { email: "approver@example.com", password: "approver1234", role: "approver" },
  { email: "editor@example.com", password: "editor1234", role: "editor" },
  { email: "viewer@example.com", password: "viewer1234", role: "viewer" }
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("editor@example.com");
  const [password, setPassword] = useState("editor1234");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const result = await login(email, password);
      setBrowserAccessToken(result.access_token);
      router.push("/dashboard");
      router.refresh();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <section className="panel w-full max-w-md p-8">
        <p className="text-xs uppercase tracking-[0.3em] text-spruce">Sign In</p>
        <h1 className="mt-3 font-display text-4xl">Welcome back</h1>
        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <input
            className="w-full rounded-2xl border border-black/10 bg-white px-4 py-3"
            placeholder="Email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <input
            className="w-full rounded-2xl border border-black/10 bg-white px-4 py-3"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          {error ? <p className="text-sm text-red-700">{error}</p> : null}
          <button className="w-full rounded-2xl bg-ink px-4 py-3 text-sm font-semibold text-white" disabled={submitting}>
            {submitting ? "Signing in..." : "Login"}
          </button>
        </form>
        <div className="mt-6 rounded-2xl bg-black/5 p-4 text-sm">
          <p className="mb-2 font-semibold">Demo accounts</p>
          <div className="space-y-1 text-ink/70">
            {demoAccounts.map((account) => (
              <p key={account.email}>
                {account.role}: {account.email} / {account.password}
              </p>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
