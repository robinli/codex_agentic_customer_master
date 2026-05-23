"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { createSystemUser, updateSystemUser } from "@/lib/api";
import { SystemUser } from "@/lib/types";

export function UsersAdmin({ users }: { users: SystemUser[] }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [roles, setRoles] = useState("viewer");
  const [error, setError] = useState<string | null>(null);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await createSystemUser({
        email,
        name,
        password,
        roles: roles.split(",").map((item) => item.trim()).filter(Boolean),
        is_active: true
      });
      router.refresh();
      setEmail("");
      setName("");
      setPassword("");
      setRoles("viewer");
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Create user failed");
    }
  }

  async function toggleUser(user: SystemUser) {
    setError(null);
    try {
      await updateSystemUser(user.id, { is_active: !user.is_active });
      router.refresh();
    } catch (toggleError) {
      setError(toggleError instanceof Error ? toggleError.message : "Update user failed");
    }
  }

  return (
    <section className="space-y-6">
      <div className="panel p-6">
        <p className="text-xs uppercase tracking-[0.25em] text-spruce">Administration</p>
        <h2 className="font-display text-4xl">Users & Roles</h2>
        <div className="mt-6 grid gap-3">
          {users.map((user) => (
            <div key={user.id} className="flex items-center justify-between rounded-2xl bg-black/5 p-4">
              <div>
                <p className="font-semibold">{user.email}</p>
                <p className="text-sm text-ink/60">
                  {user.name} - {user.roles.join(", ")} - {user.is_active ? "active" : "inactive"}
                </p>
              </div>
              <button className="rounded-2xl bg-ink px-4 py-2 text-sm font-semibold text-white" onClick={() => toggleUser(user)}>
                {user.is_active ? "Deactivate" : "Activate"}
              </button>
            </div>
          ))}
        </div>
      </div>
      <form onSubmit={handleCreate} className="panel p-6">
        <p className="text-xs uppercase tracking-[0.25em] text-spruce">Create User</p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <input className="rounded-2xl border border-black/10 bg-white px-4 py-3" placeholder="Email" value={email} onChange={(event) => setEmail(event.target.value)} />
          <input className="rounded-2xl border border-black/10 bg-white px-4 py-3" placeholder="Name" value={name} onChange={(event) => setName(event.target.value)} />
          <input className="rounded-2xl border border-black/10 bg-white px-4 py-3" placeholder="Password" value={password} onChange={(event) => setPassword(event.target.value)} />
          <input className="rounded-2xl border border-black/10 bg-white px-4 py-3" placeholder="Roles (comma separated)" value={roles} onChange={(event) => setRoles(event.target.value)} />
        </div>
        {error ? <p className="mt-4 text-sm text-red-700">{error}</p> : null}
        <button className="mt-6 rounded-2xl bg-spruce px-5 py-3 text-sm font-semibold text-white">Create User</button>
      </form>
    </section>
  );
}
