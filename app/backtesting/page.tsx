"use client";

import { useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

const historical = [
  {
    date: "2026-01-15",
    region: "Eastern DRC",
    type: "Armed Clashes",
    predictedRisk: "High",
    actualOutcome: "Conflict Escalation",
  },
  {
    date: "2025-12-02",
    region: "South Sudan Border",
    type: "Cross-border Tension",
    predictedRisk: "Medium",
    actualOutcome: "Localized Incidents",
  },
  {
    date: "2025-11-09",
    region: "Northern Syria",
    type: "Civilian Displacement",
    predictedRisk: "High",
    actualOutcome: "Major Displacement Wave",
  },
  {
    date: "2025-10-20",
    region: "Central Sahel",
    type: "Militia Movement",
    predictedRisk: "Low",
    actualOutcome: "No Escalation",
  },
];

export default function BacktestingPage() {
  const [showConfusionView, setShowConfusionView] = useState(true);

  return (
    <div className="space-y-6 bg-white">
      <h3 className="text-3xl font-semibold text-black">Backtesting Engine</h3>

      <Card>
        <CardHeader title="Date Range" subtitle="Select a historical evaluation period." />
        <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
          <input type="date" className="rounded-xl border border-gray-200 px-3 py-2 text-sm outline-none" />
          <input type="date" className="rounded-xl border border-gray-200 px-3 py-2 text-sm outline-none" />
          <Button>Apply Range</Button>
        </div>
      </Card>

      <Card>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <CardHeader title="Past Conflicts" />
          <Button
            className="bg-gray-100 text-black hover:bg-gray-200"
            onClick={() => setShowConfusionView((current) => !current)}
          >
            {showConfusionView ? "Hide" : "Show"} Confusion-style View
          </Button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-left text-gray-600">
                <th className="py-2 pr-3 font-medium">Date</th>
                <th className="py-2 pr-3 font-medium">Region</th>
                <th className="py-2 pr-3 font-medium">Type</th>
                <th className="py-2 pr-3 font-medium">Predicted Risk</th>
                <th className="py-2 font-medium">Actual Outcome</th>
              </tr>
            </thead>
            <tbody>
              {historical.map((row) => (
                <tr key={`${row.date}-${row.region}`} className="border-b border-gray-50">
                  <td className="py-2 pr-3 text-black">{row.date}</td>
                  <td className="py-2 pr-3 text-black">{row.region}</td>
                  <td className="py-2 pr-3 text-black">{row.type}</td>
                  <td className="py-2 pr-3">
                    <Badge variant={row.predictedRisk === "High" ? "primary" : "neutral"}>
                      {row.predictedRisk}
                    </Badge>
                  </td>
                  <td className="py-2 text-black">{row.actualOutcome}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {showConfusionView ? (
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl bg-[#009EDB]/10 p-4">
              <p className="text-xs uppercase text-[#009EDB]">Successful Predictions</p>
              <p className="mt-2 text-2xl font-semibold text-black">78%</p>
            </div>
            <div className="rounded-xl bg-gray-100 p-4">
              <p className="text-xs uppercase text-gray-600">Misses / False Signals</p>
              <p className="mt-2 text-2xl font-semibold text-black">22%</p>
            </div>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
