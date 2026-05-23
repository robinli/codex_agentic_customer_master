export type CustomerListItem = {
  id: string;
  customer_code: string;
  customer_name: string;
  tax_id?: string | null;
  customer_type: string;
  status: string;
  phone?: string | null;
  email?: string | null;
  updated_at: string;
};

export type CustomerContact = {
  id: string;
  name: string;
  title?: string | null;
  phone?: string | null;
  mobile?: string | null;
  email?: string | null;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
};

export type CustomerAddress = {
  id: string;
  address_type: string;
  postal_code?: string | null;
  city?: string | null;
  district?: string | null;
  address_line: string;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
};

export type CustomerDetail = CustomerListItem & {
  industry?: string | null;
  website?: string | null;
  payment_terms?: string | null;
  credit_limit?: string | number | null;
  sales_owner_id?: string | null;
  note?: string | null;
  created_at: string;
  created_by: string;
  updated_by: string;
  contacts: CustomerContact[];
  addresses: CustomerAddress[];
};

export type CustomerMutationResult = {
  status: string;
  message: string;
  approval_request_id?: string | null;
  data?: Record<string, unknown> | null;
};

export type CustomerPayload = {
  customer_code: string;
  customer_name: string;
  customer_type: string;
  tax_id?: string;
  status: string;
  phone?: string;
  email?: string;
  website?: string;
  industry?: string;
  payment_terms?: string;
  credit_limit?: string;
  note?: string;
};

export type ApprovalItem = {
  id: string;
  target_type: string;
  target_id: string;
  action: string;
  risk_level: string;
  status: string;
  reason: string;
  created_at: string;
  reviewed_at?: string | null;
  before_data?: Record<string, unknown> | null;
  after_data?: Record<string, unknown> | null;
};

export type AgentToolCall = {
  tool_name: string;
  status: string;
};

export type AgentSession = {
  id: string;
  user_id: string;
  title?: string | null;
  created_at: string;
  updated_at: string;
};

export type AgentMessage = {
  id: string;
  session_id: string;
  role: string;
  content: string;
  tool_name?: string | null;
  tool_args?: Record<string, unknown> | null;
  tool_result?: Record<string, unknown> | null;
  created_at: string;
};

export type AgentResponse = {
  message: string;
  tool_calls: AgentToolCall[];
  data?: Record<string, unknown> | null;
};

export type AuditLogItem = {
  id: string;
  actor_id?: string | null;
  actor_type: string;
  action: string;
  target_type: string;
  target_id?: string | null;
  before_data?: Record<string, unknown> | null;
  after_data?: Record<string, unknown> | null;
  metadata_json?: Record<string, unknown> | null;
  created_at: string;
};

export type SystemUser = {
  id: string;
  email: string;
  name: string;
  roles: string[];
  is_active: boolean;
};
