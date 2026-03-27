const endpoints = [
  {
    method: "GET",
    path: "/api/v1/risk/summary",
    curl: "curl -X GET https://angel.example.org/api/v1/risk/summary",
  },
  {
    method: "GET",
    path: "/api/v1/risk/regions?date=2026-03-27",
    curl: "curl -X GET 'https://angel.example.org/api/v1/risk/regions?date=2026-03-27'",
  },
  {
    method: "GET",
    path: "/api/v1/signals/:region",
    curl: "curl -X GET https://angel.example.org/api/v1/signals/horn-of-africa",
  },
  {
    method: "GET",
    path: "/api/v1/alerts/active",
    curl: "curl -X GET https://angel.example.org/api/v1/alerts/active",
  },
];

export default function ApiDocsPage() {
  return (
    <div className="space-y-6 bg-white">
      <h3 className="text-3xl font-semibold text-black">API & Data Access</h3>
      <p className="text-sm text-gray-600">
        Endpoints shown below are representative examples for authenticated dashboard access.
      </p>

      <div className="space-y-4">
        {endpoints.map((endpoint) => (
          <section key={endpoint.path} className="rounded-2xl border border-gray-100 bg-white p-4 shadow-soft">
            <p className="text-sm font-medium text-black">
              <span className="mr-2 rounded-md bg-[#009EDB]/10 px-2 py-1 font-semibold text-[#009EDB]">
                {endpoint.method}
              </span>
              {endpoint.path}
            </p>
            <pre className="mt-3 overflow-x-auto rounded-xl bg-gray-100 p-3 text-sm text-black">
              <code>{endpoint.curl}</code>
            </pre>
          </section>
        ))}
      </div>
    </div>
  );
}
