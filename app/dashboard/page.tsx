import { Card, CardHeader } from "@/components/ui/Card";
import { getRiskSummary } from "@/lib/api";
import { RiskChart } from "@/components/RiskChart";

const regionalRisk = [
  { label: "Africa", score: 82 },
  { label: "Middle East", score: 76 },
  { label: "South Asia", score: 61 },
  { label: "Eastern Europe", score: 49 },
  { label: "Latin America", score: 38 },
];

export default async function DashboardPage() {
  const summary = await getRiskSummary();

  return (
    <div className="space-y-6 bg-white">
      <h3 className="text-3xl font-semibold leading-tight text-black">Global Conflict Risk Overview</h3>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardHeader title="High-Risk Countries" />
          <p className="text-3xl font-semibold text-black">{summary.highRiskCountries}</p>
        </Card>
        <Card>
          <CardHeader title="Current Alerts" />
          <p className="text-3xl font-semibold text-black">{summary.currentAlerts}</p>
        </Card>
        <Card>
          <CardHeader title="Signal Anomalies" />
          <p className="text-3xl font-semibold text-black">{summary.signalAnomalies}</p>
        </Card>
        <Card>
          <CardHeader title="Coverage (%)" />
          <p className="text-3xl font-semibold text-black">{summary.coveragePercent}%</p>
        </Card>
      </section>

      <section>
        <Card>
          <CardHeader
            title="Regional Risk Levels"
            subtitle="Compact bar profile by region, normalized on a 100-point scale."
          />
          <RiskChart data={regionalRisk} />
        </Card>
      </section>
    </div>
  );
}
