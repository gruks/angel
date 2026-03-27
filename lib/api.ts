export type RiskSummary = {
  highRiskCountries: number;
  currentAlerts: number;
  signalAnomalies: number;
  coveragePercent: number;
};

export type AlertItem = {
  id: string;
  level: "HIGH" | "MEDIUM" | "LOW";
  region: string;
  timestamp: string;
  cause: string;
};

export async function getRiskSummary(): Promise<RiskSummary> {
  return Promise.resolve({
    highRiskCountries: 18,
    currentAlerts: 42,
    signalAnomalies: 11,
    coveragePercent: 94,
  });
}

export async function getAlerts(): Promise<AlertItem[]> {
  return Promise.resolve([
    {
      id: "alt-1",
      level: "HIGH",
      region: "Horn of Africa",
      timestamp: "2026-03-27T07:40:00Z",
      cause: "Arms import spike + UN veto",
    },
    {
      id: "alt-2",
      level: "MEDIUM",
      region: "Levant Corridor",
      timestamp: "2026-03-27T06:10:00Z",
      cause: "Social media hate score and food inflation rise",
    },
    {
      id: "alt-3",
      level: "LOW",
      region: "Western Sahel",
      timestamp: "2026-03-27T05:20:00Z",
      cause: "Localized light-drop clusters near border transit points",
    },
  ]);
}
