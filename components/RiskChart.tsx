type RiskItem = {
  label: string;
  score: number;
};

type RiskChartProps = {
  data: RiskItem[];
};

export function RiskChart({ data }: RiskChartProps) {
  return (
    <div className="space-y-4">
      {data.map((item) => (
        <div key={item.label} className="grid grid-cols-[140px_1fr_44px] items-center gap-3">
          <span className="text-sm font-medium text-black">{item.label}</span>
          <div className="h-3 w-full overflow-hidden rounded-full bg-gray-100">
            <div
              className="h-full rounded-full bg-gradient-to-r from-[#80d3f0] via-[#33b1e3] to-[#009EDB] transition-colors duration-200"
              style={{ width: `${item.score}%` }}
            />
          </div>
          <span className="text-sm text-gray-600">{item.score}</span>
        </div>
      ))}
    </div>
  );
}
