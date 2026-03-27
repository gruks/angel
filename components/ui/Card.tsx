import type { ReactNode } from "react";

type CardProps = {
  children: ReactNode;
  className?: string;
};

type CardHeaderProps = {
  title: string;
  subtitle?: string;
  rightSlot?: ReactNode;
};

export function Card({ children, className = "" }: CardProps) {
  return (
    <section
      className={`rounded-2xl border border-gray-100 bg-white p-5 shadow-soft transition-colors duration-200 hover:border-[#009EDB]/30 ${className}`}
    >
      {children}
    </section>
  );
}

export function CardHeader({ title, subtitle, rightSlot }: CardHeaderProps) {
  return (
    <div className="mb-4 flex items-start justify-between gap-3">
      <div>
        <h4 className="text-base font-semibold text-[#009EDB]">{title}</h4>
        {subtitle ? <p className="mt-1 text-sm text-gray-600">{subtitle}</p> : null}
      </div>
      {rightSlot}
    </div>
  );
}
