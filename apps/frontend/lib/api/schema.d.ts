export interface paths {}
export interface components {
  schemas: {
    DashboardKPIs: {
      totalSpent: number;
      balance: number;
      budgetUsagePercent: number;
      spendingByCategory: { category: string; amount: number; color: string; }[];
      topCategories: { id: string; name: string; amount: number; percentOfTotal: number; }[];
    };
    Transaction: {
      id: string;
      date: string;
      description: string;
      amount: number;
      category: { id: string; name: string; };
      account: { id: string; name: string; };
      paymentMethod: { id: string; name: string; };
    };
  };
}

