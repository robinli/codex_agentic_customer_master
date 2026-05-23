import {
  ApprovalItem,
  AgentMessage,
  AgentResponse,
  AgentSession,
  CustomerDetail,
  CustomerListItem,
  CustomerMutationResult,
  CustomerPayload,
  SystemUser
} from "@/lib/types";
import { getBrowserAccessToken } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

const DEFAULT_HEADERS: HeadersInit = {
  "Content-Type": "application/json",
  "X-User-Id": process.env.NEXT_PUBLIC_DEMO_USER_ID ?? "00000000-0000-0000-0000-000000000001",
  "X-User-Email": process.env.NEXT_PUBLIC_DEMO_USER_EMAIL ?? "editor@example.com",
  "X-User-Name": process.env.NEXT_PUBLIC_DEMO_USER_NAME ?? "Editor User",
  "X-User-Roles": process.env.NEXT_PUBLIC_DEMO_USER_ROLES ?? "editor"
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getBrowserAccessToken();
  const authHeaders = token ? { ...DEFAULT_HEADERS, Authorization: `Bearer ${token}` } : DEFAULT_HEADERS;
  const response = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    ...init,
    headers: {
      ...authHeaders,
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? "Request failed");
  }

  return (await response.json()) as T;
}

export async function login(email: string, password: string) {
  return request<{ access_token: string; token_type: string; user: { id: string; email: string; name: string; roles: string[] } }>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password })
    }
  );
}

export async function fetchCustomers(query?: string) {
  const params = new URLSearchParams({ page: "1", page_size: "20" });
  if (query) {
    params.set("q", query);
  }
  return request<{ items: CustomerListItem[]; page: number; page_size: number; total: number }>(
    `/customers?${params.toString()}`
  );
}

export async function fetchCustomer(customerId: string) {
  return request<CustomerDetail>(`/customers/${customerId}`);
}

export async function createCustomer(payload: CustomerPayload) {
  return request<CustomerDetail>("/customers", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function updateCustomer(customerId: string, payload: Partial<CustomerPayload>) {
  return request<CustomerMutationResult>(`/customers/${customerId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export async function fetchApprovals() {
  return request<ApprovalItem[]>("/approvals");
}

export async function fetchApproval(approvalId: string) {
  return request<ApprovalItem>(`/approvals/${approvalId}`);
}

export async function approveApproval(approvalId: string) {
  return request<ApprovalItem>(`/approvals/${approvalId}/approve`, {
    method: "POST"
  });
}

export async function rejectApproval(approvalId: string, comment: string) {
  return request<ApprovalItem>(`/approvals/${approvalId}/reject`, {
    method: "POST",
    body: JSON.stringify({ comment })
  });
}

export async function fetchAgentSessions() {
  return request<AgentSession[]>("/agent/sessions");
}

export async function createAgentSession(title?: string) {
  return request<AgentSession>("/agent/sessions", {
    method: "POST",
    body: JSON.stringify({ title: title ?? null })
  });
}

export async function fetchAgentMessages(sessionId: string) {
  return request<AgentMessage[]>(`/agent/sessions/${sessionId}/messages`);
}

export async function sendAgentMessage(sessionId: string, message: string) {
  return request<AgentResponse>(`/agent/sessions/${sessionId}/messages`, {
    method: "POST",
    body: JSON.stringify({ message })
  });
}

export async function createSystemUser(payload: {
  email: string;
  name: string;
  roles: string[];
  password: string;
  is_active?: boolean;
}) {
  return request<SystemUser>("/settings/users", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function updateSystemUser(
  userId: string,
  payload: {
    name?: string;
    roles?: string[];
    password?: string;
    is_active?: boolean;
  }
) {
  return request<SystemUser>(`/settings/users/${userId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}
