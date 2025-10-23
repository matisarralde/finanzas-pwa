import * as React from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-xl border bg-white text-foreground shadow-sm", className)} {...props} />;
}
export function CardHeader(props: React.HTMLAttributes<HTMLDivElement>) { return <div className={cn("p-6 pb-2", props.className)} {...props} />; }
export function CardTitle(props: React.HTMLAttributes<HTMLHeadingElement>) { return <h3 className={cn("text-lg font-semibold leading-none tracking-tight", props.className)} {...props} />; }
export function CardDescription(props: React.HTMLAttributes<HTMLParagraphElement>) { return <p className={cn("text-sm text-gray-500", props.className)} {...props} />; }
export function CardContent(props: React.HTMLAttributes<HTMLDivElement>) { return <div className={cn("p-6 pt-0", props.className)} {...props} />; }
export function CardFooter(props: React.HTMLAttributes<HTMLDivElement>) { return <div className={cn("p-6 pt-0", props.className)} {...props} />; }

