import { cookies } from "next/headers";

import { AUTH_COOKIE_NAME } from "@/lib/auth";
import { ApprovalItem, AuditLogItem, CustomerDetail, CustomerListItem, SystemUser } from "@/lib/types";

const SERVER_API_BASE = process.env.API_BASE_URL_SERVER ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function serverRequest<T>(path: string): Promise<T> {
  const cookieStore = await cookies();
  const token = cookieStore.get(AUTH_COOKIE_NAME)?.value ?? null;
  const response = await fetch(`${SERVER_API_BASE}${path}`, {
    cache: "no-store",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined
  });
  if (!response.ok) {
    throw new Error("Server request failed");
  }
  return (await response.json()) as T;
}

export async function fetchCustomersServer(query?: string) {
  const params = new URLSearchParams({ page: "1", page_size: "20" });
  if (query) {
    params.set("q", query);
  }
  return serverRequest<{ items: CustomerListItem[]; page: number; page_size: number; total: number }>(
    `/customers?${params.toString()}`
  );
}

export async function fetchCustomerServer(customerId: string) {
  return serverRequest<CustomerDetail>(`/customers/${customerId}`);
}

export async function fetchApprovalsServer() {
  return serverRequest<ApprovalItem[]>("/approvals");
}

export async function fetchApprovalServer(approvalId: string) {
  return serverRequest<ApprovalItem>(`/approvals/${approvalId}`);
}

export async function fetchAuditLogsServer() {
  return serverRequest<AuditLogItem[]>("/audit-logs");
}

export async function fetchSystemUsersServer() {
  return serverRequest<SystemUser[]>("/settings/users");
}
