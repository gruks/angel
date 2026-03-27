import type { ReactNode } from "react";

type BadgeVariant = "primary" | "neutral";

type BadgeProps = {
  children: ReactNode;
  variant?: BadgeVariant;
  className?: string;
};

const badgeStyles: Record<BadgeVariant, string> = {
  primary: "bg-[#009EDB]/10 text-[#009EDB]",
  neutral: "bg-gray-100 text-gray-700",
};

export function Badge({ children, variant = "neutral", className = "" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${badgeStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
