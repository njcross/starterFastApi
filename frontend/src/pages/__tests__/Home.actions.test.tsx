// src/pages/__tests__/Home.actions.test.tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

// 👇 match how Home imports:  import { api } from "../utils/api"
vi.mock("../../utils/api", () => {
  return {
    api: {
      health: vi.fn().mockResolvedValue({ ok: true }),
      pingRedis: vi.fn().mockResolvedValue({ redis: "world" }),
      dbVersion: vi.fn().mockResolvedValue({ postgres_version: "15.x" }),
    },
  };
});

import { api } from "../../utils/api";
import Home from "../Home";

describe("Home button actions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("logs success for health, ping-redis, and db-version", async () => {
    render(<Home />);

    fireEvent.click(screen.getByRole("button", { name: /health/i }));
    fireEvent.click(screen.getByRole("button", { name: /ping redis/i }));
    fireEvent.click(screen.getByRole("button", { name: /db version/i }));

    await waitFor(() => {
      // three log lines should appear
      const items = screen.getAllByRole("listitem");
      expect(items.length).toBeGreaterThanOrEqual(3);
    });

    expect(api.health).toHaveBeenCalledTimes(1);
    expect(api.pingRedis).toHaveBeenCalledTimes(1);
    expect(api.dbVersion).toHaveBeenCalledTimes(1);

    // sanity: confirm success log text shows up
    const logText = screen.getByText(/✅ health:/i);
    expect(logText).toBeInTheDocument();
  });

  it("logs an error when an API call rejects", async () => {
    (api.pingRedis as any).mockRejectedValueOnce(new Error("boom"));

    render(<Home />);

    fireEvent.click(screen.getByRole("button", { name: /ping redis/i }));

    await waitFor(() => {
      const items = screen.getAllByRole("listitem");
      expect(items[0].textContent).toMatch(/❌ ping-redis: .*boom/i);
    });
  });

  it("logs an error when an API call rejects", async () => {
    (api.health as any).mockRejectedValueOnce(new Error("boom"));

    render(<Home />);

    fireEvent.click(screen.getByRole("button", { name: /health/i }));

    await waitFor(() => {
      const items = screen.getAllByRole("listitem");
      expect(items[0].textContent).toMatch(/❌ health: .*boom/i);
    });
  });

  it("logs an error when an API call rejects", async () => {
    (api.dbVersion as any).mockRejectedValueOnce(new Error("boom"));

    render(<Home />);

    fireEvent.click(screen.getByRole("button", { name: /DB Version/i }));

    await waitFor(() => {
      const items = screen.getAllByRole("listitem");
      expect(items[0].textContent).toMatch(/❌ db-version: .*boom/i);
    });
  });
});
