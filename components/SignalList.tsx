"use client";

import { Activity, BellRing, ShieldAlert, TrendingDown, Users } from "lucide-react";

const iconMap = {
  Activity,
  BellRing,
  ShieldAlert,
  TrendingDown,
  Users,
} as const;

export type SignalItem = {
  id: string;
  name: string;
  description: string;
  predictorStrength: string;
  icon: keyof typeof iconMap;
  values: number[];
};

type SignalListProps = {
  signals: SignalItem[];
  selectedId: string;
  onSelect: (id: string) => void;
};

export function SignalList({ signals, selectedId, onSelect }: SignalListProps) {
  return (
    <div className="space-y-2">
      {signals.map((signal) => {
        const Icon = iconMap[signal.icon];
        const selected = signal.id === selectedId;

        return (
          <button
            key={signal.id}
            type="button"
            onClick={() => onSelect(signal.id)}
            className={`flex w-full items-center gap-3 rounded-xl border px-3 py-2 text-left transition-colors duration-200 ${
              selected
                ? "border-[#009EDB] bg-[#009EDB]/5"
                : "border-gray-100 bg-white hover:border-[#009EDB]/40 hover:bg-[#009EDB]/5"
            }`}
          >
            <span className="rounded-lg bg-[#009EDB]/10 p-2 text-[#009EDB]">
              <Icon size={16} />
            </span>
            <span className="text-sm font-medium text-black">{signal.name}</span>
          </button>
        );
      })}
    </div>
  );
}
