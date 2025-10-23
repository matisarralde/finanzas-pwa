import { useQuery, useMutation, QueryClient } from "@tanstack/react-query";
import { components } from "./schema";

const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS === "true";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 1000 * 60 * 5, retry: 1 } },
});

type DashboardData = components["schemas"]["DashboardKPIs"];
type Transaction = components["schemas"]["Transaction"];

const mockDashboardData: DashboardData = {
  totalSpent: 450000,
  balance: 150000,
  budgetUsagePercent: 0.75,
  spendingByCategory: [
    { category: "Comida", amount: 150000, color: "#3b82f6" },
    { category: "Transporte", amount: 80000, color: "#10b981" },
    { category: "Cuentas", amount: 120000, color: "#f97316" },
    { category: "Ocio", amount: 100000, color: "#ec4899" }
  ],
  topCategories: [
    { id: "1", name: "Comida", amount: 150000, percentOfTotal: 0.33 },
    { id: "2", name: "Cuentas", amount: 120000, percentOfTotal: 0.26 },
    { id: "3", name: "Ocio", amount: 100000, percentOfTotal: 0.22 }
  ]
};

const mockTransactions: Transaction[] = [
  { id: "t1", date: new Date().toISOString(), description: "Supermercado Lider", amount: 75000, category: { id: "c1", name: "Comida" }, account: { id: "a1", name: "Cuenta Corriente" }, paymentMethod: { id: "p1", name: "Débito" } },
  { id: "t2", date: new Date().toISOString(), description: "Pago CGE", amount: 45000, category: { id: "c2", name: "Cuentas" }, account: { id: "a1", name: "Cuenta Corriente" }, paymentMethod: { id: "p1", name: "Débito" } },
  { id: "t3", date: new Date().toISOString(), description: "Carga Bip!", amount: 10000, category: { id: "c3", name: "Transporte" }, account: { id: "a2", name: "Efectivo" }, paymentMethod: { id: "p2", name: "Efectivo" } }
];

const apiFetch = async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
  const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  if (!res.ok) throw new Error((await res.json()).message || "Error API");
  return res.json() as Promise<T>;
};

export const useDashboardData = (month: string) => {
  return useQuery<DashboardData, Error>({
    queryKey: ["dashboard", month],
    queryFn: async () => {
      if (USE_MOCKS) { await new Promise(r => setTimeout(r, 400)); return mockDashboardData; }
      return apiFetch<DashboardData>(`/dashboard?month=${month}`);
    },
  });
};

export const useTransactions = (filters: { month: string; category?: string; account?: string; }) => {
  const queryParams = new URLSearchParams(filters as Record<string, string>).toString();
  return useQuery<Transaction[], Error>({
    queryKey: ["transactions", filters],
    queryFn: async () => {
      if (USE_MOCKS) { await new Promise(r => setTimeout(r, 400)); return mockTransactions; }
      return apiFetch<Transaction[]>(`/transactions?${queryParams}`);
    },
  });
};

export const useUpdateTransaction = () => {
  return useMutation<Transaction, Error, Partial<Transaction> & { id: string }>({
    mutationFn: async (updated) => {
      if (USE_MOCKS) {
        await new Promise(r => setTimeout(r, 200));
        const i = mockTransactions.findIndex(t => t.id === updated.id);
        if (i > -1) { /* @ts-ignore */ mockTransactions[i] = { ...mockTransactions[i], ...updated }; return mockTransactions[i]; }
        throw new Error("Transacción no encontrada");
      }
      const { id, ...payload } = updated;
      return apiFetch<Transaction>(`/transactions/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    }
  });
};

