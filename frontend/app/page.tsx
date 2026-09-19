"use client";

import { useEffect, useState } from "react";

type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

type FetchState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "success"; data: HealthResponse };

export default function Home() {
  const [state, setState] = useState<FetchState>({ kind: "loading" });

  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Request failed with status ${res.status}`);
        }
        return res.json() as Promise<HealthResponse>;
      })
      .then((data) => setState({ kind: "success", data }))
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Unknown error";
        setState({ kind: "error", message });
      });
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-6 text-2xl font-bold text-gray-900">InboxOps</h1>

        {state.kind === "loading" && (
          <p className="text-gray-600">Connecting to API…</p>
        )}

        {state.kind === "error" && (
          <p className="text-red-600">{state.message}</p>
        )}

        {state.kind === "success" && (
          <div className="space-y-1">
            <p className="text-green-600">status: {state.data.status}</p>
            <p className="text-gray-800">service: {state.data.service}</p>
            <p className="text-gray-800">version: {state.data.version}</p>
          </div>
        )}
      </div>
    </div>
  );
}
