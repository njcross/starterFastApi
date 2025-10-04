// src/utils/__tests__/api.test.ts
import { describe, it, expect, vi, afterEach } from "vitest";
import { api } from "../api";

const g: any = globalThis;

describe("api helpers", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("health succeeds when res.ok", async () => {
    vi.spyOn(g, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ok: true }),
    } as any);

    await expect(api.health()).resolves.toEqual({ ok: true });
    expect(g.fetch).toHaveBeenCalledWith("/api/health");
  });

  it("health throws when !res.ok", async () => {
    vi.spyOn(g, "fetch").mockResolvedValueOnce({ ok: false, status: 503 } as any);
    await expect(api.health()).rejects.toThrow("Health failed: 503");
  });

  it("pingRedis succeeds / fails", async () => {
    vi.spyOn(g, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({ redis: "world" }),
    } as any);
    await expect(api.pingRedis()).resolves.toEqual({ redis: "world" });

    vi.spyOn(g, "fetch").mockResolvedValueOnce({ ok: false, status: 500 } as any);
    await expect(api.pingRedis()).rejects.toThrow("Ping failed: 500");
  });

  it("dbVersion succeeds / fails", async () => {
    vi.spyOn(g, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({ postgres_version: "15.x" }),
    } as any);
    await expect(api.dbVersion()).resolves.toEqual({ postgres_version: "15.x" });

    vi.spyOn(g, "fetch").mockResolvedValueOnce({ ok: false, status: 418 } as any);
    await expect(api.dbVersion()).rejects.toThrow("DB version failed: 418");
  });
});
