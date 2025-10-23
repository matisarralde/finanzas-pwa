"use client";

import React, { useState, useEffect } from "react";
import MonthSelector from "@/components/MonthSelector";
import { useRouter } from "next/navigation";
import { LayoutDashboard, CreditCard, Settings, CircleDollarSign, PieChart, BookUser, Plus } from "lucide-react";
import { CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator } from "@/components/ui/command";

function Navbar({ onOpenKbar }: { onOpenKbar: () => void }) {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        <div className="mr-4 hidden md:flex">
          <a href="/dashboard" className="mr-6 flex items-center space-x-2">
            <PieChart className="h-6 w-6" />
            <span className="hidden font-bold sm:inline-block">
              {process.env.NEXT_PUBLIC_APP_NAME}
            </span>
          </a>
          <nav className="flex items-center gap-6 text-sm">
            <a href="/dashboard" className="text-foreground/60 hover:text-foreground/80">Dashboard</a>
            <a href="/transactions" className="text-foreground/60 hover:text-foreground/80">Transacciones</a>
            <a href="/budgets" className="text-foreground/60 hover:text-foreground/80">Presupuestos</a>
            <a href="/accounts" className="text-foreground/60 hover:text-foreground/80">Cuentas</a>
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <div className="w-full flex-1 md:w-auto md:flex-none">
            <MonthSelector />
          </div>
          <nav className="flex items-center">
            <button onClick={onOpenKbar} className="p-2 rounded-md hover:bg-gray-100" aria-label="Abrir búsqueda">
              <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-gray-100 px-1.5 font-mono text-[10px] font-medium text-gray-600">
                <span className="text-xs">⌘</span>K
              </kbd>
            </button>
            <a href="/settings" className="p-2 rounded-md hover:bg-gray-100">
              <Settings className="h-5 w-5" />
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
}

export default function MainAppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [openKbar, setOpenKbar] = useState(false);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpenKbar((open) => !open);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const runCommand = (cb: () => void) => {
    setOpenKbar(false);
    cb();
  };

  return (
    <div className="relative flex min-h-screen flex-col">
      <Navbar onOpenKbar={() => setOpenKbar(true)} />
      <main className="flex-1 container max-w-screen-2xl py-6">{children}</main>

      <CommandDialog open={openKbar} onOpenChange={setOpenKbar}>
        <CommandInput placeholder="Escribe un comando o busca..." />
        <CommandList>
          <CommandEmpty>No se encontraron resultados.</CommandEmpty>
          <CommandGroup heading="Acciones Rápidas">
            <CommandItem onSelect={() => runCommand(() => alert("Abrir: Agregar Gasto"))}>
              <Plus className="mr-2 h-4 w-4" /> <span>Agregar Gasto</span>
            </CommandItem>
            <CommandItem onSelect={() => runCommand(() => alert("Abrir: Crear Regla"))}>
              <PieChart className="mr-2 h-4 w-4" /> <span>Crear Regla</span>
            </CommandItem>
          </CommandGroup>
          <CommandGroup heading="Navegación">
            <CommandItem onSelect={() => runCommand(() => router.push("/dashboard"))}>
              <LayoutDashboard className="mr-2 h-4 w-4" /> <span>Dashboard</span>
            </CommandItem>
            <CommandItem onSelect={() => runCommand(() => router.push("/transactions"))}>
              <CircleDollarSign className="mr-2 h-4 w-4" /> <span>Transacciones</span>
            </CommandItem>
            <CommandItem onSelect={() => runCommand(() => router.push("/budgets"))}>
              <PieChart className="mr-2 h-4 w-4" /> <span>Presupuestos</span>
            </CommandItem>
            <CommandItem onSelect={() => runCommand(() => router.push("/categories-rules"))}>
              <BookUser className="mr-2 h-4 w-4" /> <span>Categorías y Reglas</span>
            </CommandItem>
            <CommandItem onSelect={() => runCommand(() => router.push("/accounts"))}>
              <CreditCard className="mr-2 h-4 w-4" /> <span>Cuentas</span>
            </CommandItem>
            <CommandItem onSelect={() => runCommand(() => router.push("/settings"))}>
              <Settings className="mr-2 h-4 w-4" /> <span>Configuración</span>
            </CommandItem>
          </CommandGroup>
          <CommandSeparator />
        </CommandList>
      </CommandDialog>
    </div>
  );
}

