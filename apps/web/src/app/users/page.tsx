"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { StatusChip } from "../components/ui/StatusChip";
import { EmptyState } from "../components/ui/EmptyState";
import type { User } from "@/types/api";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [deptFilter, setDeptFilter] = useState("");

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (search) params.query = search;
      if (deptFilter) params.department = deptFilter;
      const result = await api.searchUsers(params);
      setUsers(result);
    } catch {
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadUsers();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Users</h1>

      <form onSubmit={handleSearch} className="flex gap-3 mb-6">
        <input
          type="text"
          placeholder="Search by name, email, or employee ID..."
          className="input flex-1"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="input w-48"
          value={deptFilter}
          onChange={(e) => { setDeptFilter(e.target.value); }}
        >
          <option value="">All Departments</option>
          <option value="Corporate Finance">Corporate Finance</option>
          <option value="IT Operations">IT Operations</option>
          <option value="Product Engineering">Product Engineering</option>
          <option value="Health Informatics">Health Informatics</option>
          <option value="Human Resources">Human Resources</option>
          <option value="Information Security">Information Security</option>
          <option value="Nursing - ICU">Nursing - ICU</option>
        </select>
        <button type="submit" className="btn-primary">Search</button>
      </form>

      {loading ? (
        <LoadingSpinner />
      ) : users.length === 0 ? (
        <EmptyState message="No users found. Try syncing data first." />
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Name</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Email</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Department</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Job Title</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">State</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Type</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <Link href={`/users/${user.id}`} className="text-primary-600 hover:underline font-medium">
                      {user.display_name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{user.email}</td>
                  <td className="px-4 py-3 text-gray-600">{user.department || "-"}</td>
                  <td className="px-4 py-3 text-gray-600">{user.job_title || "-"}</td>
                  <td className="px-4 py-3"><StatusChip status={user.lifecycle_state} /></td>
                  <td className="px-4 py-3 text-gray-600 capitalize">{user.worker_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
