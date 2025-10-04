// frontend/src/pages/__tests__/Home.setLog.test.tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock the same module Home imports
vi.mock("../../utils/api", () => ({
  api: {
    health: vi.fn(),
    pingRedis: vi.fn(),
    dbVersion: vi.fn(),
  },
}));

import { api } from "../../utils/api";
import Home from "../Home";

describe("Home.setLog coverage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("hits success branch and renders exact JSON string (covers the setLog success line)", async () => {
    (api.health as any).mockResolvedValueOnce({ ok: true, v: 1 });

    render(<Home />);

    // Click Health -> triggers run("health", api.health)
    fireEvent.click(screen.getByRole("button", { name: /health/i }));

    // Expect the exact formatted success entry (ensures JSON.stringify(data) path is executed)
    const expected = `✅ health: ${JSON.stringify({ ok: true, v: 1 })}`;
    await waitFor(() => {
      expect(screen.getByText(expected)).toBeInTheDocument();
    });
  });

  it("hits error fallback when error has no .message (covers e?.message ?? e)", async () => {
    // Reject with a primitive so e.message is undefined
    (api.pingRedis as any).mockRejectedValueOnce("totally-broken");

    render(<Home />);

    fireEvent.click(screen.getByRole("button", { name: /ping redis/i }));

    await waitFor(() => {
      // Should use the right-hand side of the ?? operator (the value itself)
      // and render the error log entry
      const items = screen.getAllByRole("listitem");
      expect(items[0].textContent).toMatch(/❌ ping-redis: .*totally-broken/i);
    });
  });
});
