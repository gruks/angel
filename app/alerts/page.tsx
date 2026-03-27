import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { getAlerts } from "@/lib/api";

const filters = ["All", "High-Priority", "Resolved"];

export default async function AlertsPage() {
  const alerts = await getAlerts();

  return (
    <div className="space-y-6 bg-white">
      <h3 className="text-3xl font-semibold text-black">Active Alerts</h3>

      <div className="flex flex-wrap gap-2">
        {filters.map((filter, index) => (
          <button
            key={filter}
            type="button"
            className={`rounded-full px-3 py-1 text-sm transition-colors duration-200 ${
              index === 0 ? "bg-[#009EDB] text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {filter}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {alerts.map((alert) => (
          <Card key={alert.id} className="hover:bg-[#009EDB]/[0.02]">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant={alert.level === "HIGH" ? "primary" : "neutral"}>
                    {alert.level} RISK
                  </Badge>
                  <span className="text-sm text-gray-600">{new Date(alert.timestamp).toLocaleString()}</span>
                </div>
                <h4 className="text-lg font-semibold text-black">{alert.region}</h4>
                <p className="text-sm text-gray-600">{alert.cause}</p>
              </div>
              <div className="flex items-center gap-2">
                <Button className="bg-gray-100 text-black hover:bg-gray-200">Acknowledge</Button>
                <Button href="/signals">See Details</Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
