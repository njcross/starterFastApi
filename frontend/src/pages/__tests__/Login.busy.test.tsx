// frontend/src/pages/__tests__/Login.busy.test.tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, beforeEach } from "vitest";
import Login from "../Login";

// A controllable promise to keep fetch pending until we resolve it manually
function deferred<T>() {
  let resolve!: (v: T) => void;
  const p = new Promise<T>((res) => (resolve = res));
  return { promise: p, resolve };
}

describe("Login busy state", () => {
  beforeEach(() => {
    // reset fetch between tests
    (global.fetch as any) = undefined;
  });

  it('shows "Sending…" and disables the button while request is in flight, then restores', async () => {
    const def = deferred<Response>();

    // mock fetch to stay pending until we call def.resolve(...)
    (global.fetch as any) = vi.fn().mockImplementation(() => def.promise);

    render(<Login />);

    // fill in email
    await userEvent.type(screen.getByPlaceholderText(/you@example\.com/i), "person@example.com");

    // click submit (starts sendLink → sets busy=true and awaits fetch)
    const btn = screen.getByRole("button", { name: /send magic link/i });
    await userEvent.click(btn);

    // While fetch is pending, button should be disabled and label should flip to "Sending…"
    await waitFor(() => {
      // The original "Send magic link" text should disappear and "Sending…" should appear
      expect(screen.queryByRole("button", { name: /send magic link/i })).not.toBeInTheDocument();
      expect(screen.getByRole("button", { name: /sending…/i })).toBeDisabled();
    });

    // Now resolve the request to a successful response
    def.resolve({
      ok: true,
      json: async () => ({ sent: true }),
    } as any);

    // After the promise resolves, UI should return to normal label and re-enable the button
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /send magic link/i })).toBeEnabled();
    });

    // Optional: success message appears
    expect(await screen.findByText(/we’ve sent a sign-in link/i)).toBeInTheDocument();

    // And fetch was called with expected payload
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/auth/request-link",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
    );
  });
});
