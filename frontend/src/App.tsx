import React, { useState } from "react";
import { api } from "./api";

export default function App() {
  const [log, setLog] = useState<string[]>([]);

  const run = async (label: string, fn: () => Promise<any>) => {
    try {
      const data = await fn();
      setLog((l) => [`✅ ${label}: ${JSON.stringify(data)}`, ...l]);
    } catch (e: any) {
      setLog((l) => [`❌ ${label}: ${e?.message ?? e}`, ...l]);
    }
  };

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: 24, maxWidth: 800 }}>
      <h1>Five Eyes Cyber Hygiene (Frontend TS)</h1>
      <p>Try hitting the Flask API via the Vite proxy:</p>
      <div style={{ display: "flex", gap: 12, margin: "12px 0" }}>
        <button onClick={() => run("health", api.health)}>Health</button>
        <button onClick={() => run("ping-redis", api.pingRedis)}>Ping Redis</button>
        <button onClick={() => run("db-version", api.dbVersion)}>DB Version</button>
      </div>
      <ul>
        {log.map((line, i) => (
          <li key={i} style={{ fontFamily: "monospace" }}>{line}</li>
        ))}
      </ul>
    </main>
  );
}
