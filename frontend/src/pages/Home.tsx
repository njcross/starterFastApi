import React, { useState } from "react";
import Button from "../components/Button";
import { api } from "../utils/api";

export default function Home() {
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
    <section>
      <h1>Five Eyes Cyber Hygiene (Frontend TS)</h1>
      <p>Try hitting the Flask API via the Vite proxy:</p>
      <div className="row">
        <Button onClick={() => run("health", api.health)}>Health</Button>
        <Button onClick={() => run("ping-redis", api.pingRedis)}>Ping Redis</Button>
        <Button onClick={() => run("db-version", api.dbVersion)}>DB Version</Button>
      </div>

      <ul className="log">
        {log.map((line, i) => (
          <li key={i}><code>{line}</code></li>
        ))}
      </ul>
    </section>
  );
}
