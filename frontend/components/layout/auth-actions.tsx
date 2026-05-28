"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { clearBrowserAccessToken, getBrowserAccessToken } from "@/lib/auth";

export function AuthActions({ initialHasToken = false }: { initialHasToken?: boolean }) {
  const router = useRouter();
  const [hasToken, setHasToken] = useState(initialHasToken);

  useEffect(() => {
    setHasToken(Boolean(getBrowserAccessToken()));
  }, []);

  function handleLogout() {
    clearBrowserAccessToken();
    setHasToken(false);
    router.push("/login");
    router.refresh();
  }

  if (!hasToken) {
    return (
      <Link
        href="/login"
        className="block rounded-2xl border border-black/10 px-4 py-3 text-center text-sm font-semibold text-ink transition hover:border-spruce hover:bg-spruce hover:text-white"
      >
        Login
      </Link>
    );
  }

  return (
    <button
      type="button"
      onClick={handleLogout}
      className="w-full rounded-2xl border border-black/10 px-4 py-3 text-sm font-semibold text-ink transition hover:border-spruce hover:bg-spruce hover:text-white"
    >
      Logout
    </button>
  );
}
