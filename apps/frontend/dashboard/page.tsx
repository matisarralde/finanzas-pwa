"use client";

import { useSearchParams } from "next/navigation";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { useDashboardData } from "@/lib/api/client";
import { formatCurrency } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, TrendingDown, CircleDollarSign, Target } from "lucide-react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import MainAppLayout from "@/components/MainAppLayout";

function KpiCards({ data, isLoading }: { data?: any; isLoading: boolean }) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }
  if (!data) return null;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Balance del Mes</CardTitle>
          <CircleDollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(data.balance)}</div>
          <p className="text-xs text-muted-foreground">
            {data.balance > 0 ? "Positivo este mes" : "Negativo este mes"}
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Gasto Total</CardTitle>
          <TrendingDown className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(data.totalSpent)}</div>
          <p className="text-xs text-muted-foreground">+5.2% vs mes anterior</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Presupuesto Usado</CardTitle>
          <Target className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{Math.round(data.budgetUsagePercent * 100)}%</div>
          <p className="text-xs text-muted-foreground">
            {formatCurrency(data.totalSpent)} de {formatCurrency(data.totalSpent / data.budgetUsagePercent)}
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Categoría Principal</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{data.topCategories[0]?.name || "N/A"}</div>
          <p className="text-xs text-muted-foreground">
            {formatCurrency(data.topCategories[0]?.amount)}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

function SpendingChart({ data, isLoading }: { data?: any; isLoading: boolean }) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader><CardTitle>Gastos por Categoría</CardTitle></CardHeader>
        <CardContent><Skeleton className="h-[350px] w-full" /></CardContent>
      </Card>
    );
  }
  if (!data) return null;

  return (
    <Card>
      <CardHeader><CardTitle>Gastos por Categoría</CardTitle></CardHeader>
      <CardContent className="pl-0">
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={data.spendingByCategory}>
            <XAxis dataKey="category" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false}
              tickFormatter={(value) => `${formatCurrency(value)}`} />
            <Tooltip cursor={{ fill: "transparent" }} contentStyle={{
              backgroundColor: "hsl(var(--background))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "var(--radius)" }} />
            <Bar dataKey="amount" fill="var(--theme-primary)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function TopCategoriesTable({ data, isLoading }: { data?: any; isLoading: boolean }) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader><CardTitle>Categorías Principales</CardTitle></CardHeader>
        <CardContent><div className="space-y-4"><Skeleton className="h-8 w-full" /><Skeleton className="h-8 w-full" /><Skeleton className="h-8 w-full" /></div></CardContent>
      </Card>
    );
  }
  if (!data) return null;

  return (
    <Card>
      <CardHeader><CardTitle>Categorías Principales</CardTitle></CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Categoría</TableHead>
              <TableHead className="text-right">Monto</TableHead>
              <TableHead className="text-right">% del Total</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.topCategories.map((category: any) => (
              <TableRow key={category.id}>
                <TableCell className="font-medium">{category.name}</TableCell>
                <TableCell className="text-right">{formatCurrency(category.amount)}</TableCell>
                <TableCell className="text-right">{Math.round(category.percentOfTotal * 100)}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const month = searchParams.get("month") || format(new Date(), "yyyy-MM");
  const { data, isLoading, isError, error } = useDashboardData(month);
  const formattedMonth = format(new Date(`${month}-02`), "MMMM yyyy", { locale: es });

  if (isError) return <div className="text-red-600">Error al cargar datos: {String(error.message)}</div>;

  return (
    <MainAppLayout>
      <div className="flex-1 space-y-6">
        <h2 className="text-3xl font-bold tracking-tight capitalize">Dashboard: {formattedMonth}</h2>
        <KpiCards data={data} isLoading={isLoading} />
        <div className="grid gap-6 md:grid-cols-2">
          <SpendingChart data={data} isLoading={isLoading} />
          <TopCategoriesTable data={data} isLoading={isLoading} />
        </div>
      </div>
    </MainAppLayout>
  );
}

