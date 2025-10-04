// src/contexts/__tests__/UserContext.test.tsx
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import React from "react";
import { UserProvider, useUser } from "../UserContext";

const TestConsumer = () => {
  const { currentUser, logout } = useUser();
  return (
    <div>
      <div data-testid="email">{currentUser?.email ?? "none"}</div>
      <button onClick={logout}>logout</button>
    </div>
  );
};

describe("UserContext", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    // default global fetch
    (global as any).fetch = vi.fn();
  });

  it("sets user from /api/auth/me on mount", async () => {
    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ user: { id: 1, email: "a@b.com" } }),
    });

    render(
      <UserProvider>
        <TestConsumer />
      </UserProvider>
    );

    await waitFor(() =>
      expect(screen.getByTestId("email").textContent).toBe("a@b.com")
    );
  });

  it("handles fetch error and sets user=null", async () => {
    (fetch as any).mockRejectedValueOnce(new Error("boom"));

    render(
      <UserProvider>
        <TestConsumer />
      </UserProvider>
    );

    await waitFor(() =>
      expect(screen.getByTestId("email").textContent).toBe("none")
    );
  });

  it("logout calls /api/auth/logout and clears user", async () => {
    // initial GET /me success
    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ user: { id: 1, email: "c@d.com" } }),
    });
    // POST /logout
    ;(fetch as any).mockResolvedValueOnce({ ok: true, json: async () => ({ ok: true }) });

    render(
      <UserProvider>
        <TestConsumer />
      </UserProvider>
    );

    await waitFor(() =>
      expect(screen.getByTestId("email").textContent).toBe("c@d.com")
    );

    // click logout
    screen.getByText(/logout/i).click();

    await waitFor(() =>
      expect(screen.getByTestId("email").textContent).toBe("none")
    );

    // assert second call was logout
    expect((fetch as any).mock.calls[1][0]).toMatch(/\/api\/auth\/logout$/);
    expect((fetch as any).mock.calls[1][1]).toMatchObject({
      method: "POST",
      credentials: "include",
    });
  });
});
