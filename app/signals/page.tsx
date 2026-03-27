"use client";

import { useMemo, useState } from "react";

import { SignalList, type SignalItem } from "@/components/SignalList";
import { Card, CardHeader } from "@/components/ui/Card";

const signals: SignalItem[] = [
  {
    id: "social-hate",
    name: "Social Media Hate Score",
    description: "Captures shifts in hate-labeled language volume in regional social channels.",
    predictorStrength: "Strong predictor in urban unrest contexts.",
    icon: "Users",
    values: [38, 41, 44, 49, 53, 58, 64, 69],
  },
  {
    id: "arms-imports",
    name: "Arms Imports",
    description: "Tracks monthly import deviations against 24-month regional baselines.",
    predictorStrength: "Moderate-to-strong predictor when paired with veto events.",
    icon: "ShieldAlert",
    values: [30, 31, 33, 37, 45, 48, 52, 59],
  },
  {
    id: "un-veto",
    name: "UN Veto Count",
    description: "Measures veto concentration and temporal clustering in conflict-relevant dockets.",
    predictorStrength: "Strong predictor in institutional deadlock scenarios.",
    icon: "BellRing",
    values: [22, 22, 24, 28, 27, 33, 41, 43],
  },
  {
    id: "light-drop",
    name: "Night Light Drop",
    description: "Uses satellite-derived light attenuation as a proxy for infrastructure disruption.",
    predictorStrength: "High predictive value for rapid territorial deterioration.",
    icon: "TrendingDown",
    values: [55, 57, 56, 52, 47, 45, 43, 39],
  },
  {
    id: "market-volatility",
    name: "Staple Market Volatility",
    description: "Estimates stress from abrupt food and fuel price dislocations.",
    predictorStrength: "Moderate predictor, strongest with displacement indicators.",
    icon: "Activity",
    values: [27, 29, 33, 34, 36, 40, 43, 46],
  },
];

function TinyLineChart({ values }: { values: number[] }) {
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  const points = values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * 100;
      const y = 100 - ((value - min) / range) * 100;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg viewBox="0 0 100 100" className="h-44 w-full rounded-xl border border-gray-100 bg-white p-3">
      <polyline fill="none" stroke="#009EDB" strokeWidth="2.5" points={points} />
    </svg>
  );
}

export default function SignalsPage() {
  const [selectedId, setSelectedId] = useState(signals[0].id);
  const selectedSignal = useMemo(
    () => signals.find((signal) => signal.id === selectedId) ?? signals[0],
    [selectedId],
  );

  return (
    <div className="space-y-6 bg-white">
      <h3 className="text-3xl font-semibold text-black">Signal Explorer</h3>
      <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
        <Card>
          <CardHeader title="Signal Types" subtitle="Select a signal stream to inspect trend and influence." />
          <SignalList signals={signals} selectedId={selectedSignal.id} onSelect={setSelectedId} />
        </Card>

        <Card>
          <CardHeader title={selectedSignal.name} subtitle={selectedSignal.description} />
          <TinyLineChart values={selectedSignal.values} />
          <p className="mt-4 text-sm text-gray-600">
            <span className="font-semibold text-black">Strength of this signal as a predictor:</span>{" "}
            {selectedSignal.predictorStrength}
          </p>
        </Card>
      </div>
    </div>
  );
}
