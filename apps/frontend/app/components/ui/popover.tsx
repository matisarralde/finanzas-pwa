"use client";
import * as React from "react";

export function Popover({ children, open, onOpenChange }: { children: React.ReactNode; open?: boolean; onOpenChange?: (o: boolean) => void; }) {
  return <div>{children}</div>;
}
export function PopoverTrigger({ asChild, children }: { asChild?: boolean; children: React.ReactNode; }) {
  return <>{children}</>;
}
export function PopoverContent({ children, className }: { children: React.ReactNode; className?: string; }) {
  return <div className={className}>{children}</div>;
}

