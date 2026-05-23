import Link from "next/link";

import { CustomerListItem } from "@/lib/types";

export function CustomerTable({ items }: { items: CustomerListItem[] }) {
  return (
    <div className="panel overflow-hidden">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-ink text-white">
          <tr>
            <th className="px-4 py-3">Code</th>
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Phone</th>
            <th className="px-4 py-3">Updated</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-t border-black/5">
              <td className="px-4 py-3">{item.customer_code}</td>
              <td className="px-4 py-3 font-medium">
                <Link href={`/customers/${item.id}`} className="hover:text-spruce hover:underline">
                  {item.customer_name}
                </Link>
              </td>
              <td className="px-4 py-3">{item.customer_type}</td>
              <td className="px-4 py-3">
                <span className="rounded-full bg-spruce/10 px-3 py-1 text-xs text-spruce">{item.status}</span>
              </td>
              <td className="px-4 py-3">{item.phone ?? "-"}</td>
              <td className="px-4 py-3">{new Date(item.updated_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
