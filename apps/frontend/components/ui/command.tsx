"use client";
import * as React from "react";

export function CommandDialog({ open, onOpenChange, children }: { open: boolean; onOpenChange: (o: boolean) => void; children: React.ReactNode; }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/30">
      <div className="mx-auto mt-24 w-full max-w-xl rounded-xl border bg-white p-2 shadow-lg">{children}</div>
      <div className="absolute inset-0" onClick={() => onOpenChange(false)} />
    </div>
  );
}
export function CommandInput(props: React.InputHTMLAttributes<HTMLInputElement>) { return <input className="w-full rounded-md border px-3 py-2" {...props} />; }
export function CommandList({ children }: { children: React.ReactNode }) { return <div className="max-h-96 overflow-auto p-1">{children}</div>; }
export function CommandEmpty({ children }: { children: React.ReactNode }) { return <div className="p-2 text-sm text-gray-500">{children}</div>; }
export function CommandGroup({ heading, children }: { heading?: string; children: React.ReactNode; }) { return <div className="p-2"><div className="px-1 pb-1 text-xs uppercase text-gray-500">{heading}</div>{children}</div>; }
export function CommandItem({ children, onSelect }: { children: React.ReactNode; onSelect?: () => void; }) { return <div className="cursor-pointer rounded-md px-2 py-1 hover:bg-gray-100" onClick={onSelect}>{children}</div>; }
export function CommandSeparator() { return <div className="my-2 border-t" />; }

