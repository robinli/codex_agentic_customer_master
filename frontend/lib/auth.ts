export const AUTH_COOKIE_NAME = "agentic_customer_master_token";

function parseCookieValue(name: string, cookieString: string): string | null {
  const prefix = `${name}=`;
  for (const part of cookieString.split(";")) {
    const item = part.trim();
    if (item.startsWith(prefix)) {
      return decodeURIComponent(item.slice(prefix.length));
    }
  }
  return null;
}

export function getBrowserAccessToken(): string | null {
  if (typeof document === "undefined") {
    return null;
  }
  return parseCookieValue(AUTH_COOKIE_NAME, document.cookie);
}

export function setBrowserAccessToken(token: string): void {
  if (typeof document === "undefined") {
    return;
  }
  document.cookie = `${AUTH_COOKIE_NAME}=${encodeURIComponent(token)}; Path=/; Max-Age=${60 * 60 * 8}; SameSite=Lax`;
}

export function clearBrowserAccessToken(): void {
  if (typeof document === "undefined") {
    return;
  }
  document.cookie = `${AUTH_COOKIE_NAME}=; Path=/; Max-Age=0; SameSite=Lax`;
}
