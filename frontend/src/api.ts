export const api = {
  async health(): Promise<{ ok: boolean }> {
    const res = await fetch("/api/health");
    if (!res.ok) throw new Error(`Health failed: ${res.status}`);
    return res.json();
  },
  async pingRedis(): Promise<{ redis: string }> {
    const res = await fetch("/api/ping-redis");
    if (!res.ok) throw new Error(`Ping failed: ${res.status}`);
    return res.json();
  },
  async dbVersion(): Promise<{ postgres_version?: string; error?: string }> {
    const res = await fetch("/api/db-version");
    if (!res.ok) throw new Error(`DB version failed: ${res.status}`);
    return res.json();
  }
};
