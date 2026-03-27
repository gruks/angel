import { MapWrapper } from "@/components/MapWrapper";
import { Tooltip } from "@/components/ui/Tooltip";

const legendStops = [
  { label: "Low Risk", color: "#d7effa" },
  { label: "Moderate", color: "#7bc9e8" },
  { label: "Elevated", color: "#2ca8de" },
  { label: "High Risk", color: "#006d96" },
];

const hoverExample = {
  region: "North Kivu Corridor",
  score: 78,
  change: "+4 points since yesterday",
};

export default function HeatmapPage() {
  return (
    <div className="space-y-4 bg-white">
      <h3 className="text-3xl font-semibold text-black">Global Risk Heatmap</h3>
      <MapWrapper className="w-full">
        <div className="absolute right-3 top-3 z-20 w-52 rounded-xl border border-gray-100 bg-white/95 p-3 shadow-soft">
          <p className="text-sm font-semibold text-[#009EDB]">Risk Legend</p>
          <div className="mt-3 space-y-2">
            {legendStops.map((stop) => (
              <div key={stop.label} className="flex items-center justify-between text-xs text-gray-600">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full" style={{ backgroundColor: stop.color }} />
                  <span>{stop.label}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="absolute bottom-4 left-4 z-20 rounded-xl border border-gray-100 bg-white/95 p-3 shadow-soft">
          <Tooltip content="Preview of region-level hover tooltip">
            <div className="cursor-help space-y-1">
              <p className="text-sm font-semibold text-black">{hoverExample.region}</p>
              <p className="text-sm text-[#009EDB]">Risk Score: {hoverExample.score}</p>
              <p className="text-xs text-gray-600">{hoverExample.change}</p>
            </div>
          </Tooltip>
        </div>
      </MapWrapper>
      <p className="text-sm text-gray-600">
        H3-style regional cells are rendered as a UN-blue gradient from low to high risk.
      </p>
    </div>
  );
}
