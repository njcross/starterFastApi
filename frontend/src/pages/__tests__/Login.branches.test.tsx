// src/pages/__tests__/Login.branches.test.tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import Login from "../Login";

const g: any = globalThis;

describe("Login branches", () => {
  beforeEach(() => {
    vi.stubEnv("VITE_API_ORIGIN", "http://localhost:8000");
    vi.restoreAllMocks();
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("handles non-200 response", async () => {
    vi.spyOn(g, "fetch").mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ error: "bad email" }),
    } as any);

    render(<Login />);

    fireEvent.change(
      screen.getByPlaceholderText("you@example.com"),
      { target: { value: "x@y.com" } },
    );
    fireEvent.click(screen.getByRole("button", { name: /send magic link/i }));

    await waitFor(() => {
      // component sets message to the error message
      expect(screen.getByText(/bad email|400/i)).toBeInTheDocument();
    });
  });

  it("handles network throw (catch path)", async () => {
    vi.spyOn(g, "fetch").mockRejectedValueOnce(new Error("network down"));

    render(<Login />);

    fireEvent.change(
      screen.getByPlaceholderText("you@example.com"),
      { target: { value: "z@z.com" } },
    );
    fireEvent.click(screen.getByRole("button", { name: /send magic link/i }));

    await waitFor(() => {
      expect(screen.getByText(/network down/i)).toBeInTheDocument();
    });
  });

  it('non-200 without "error" uses HTTP <status> fallback', async () => {
    vi.spyOn(g, "fetch").mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({}), // no { error } key -> should use "HTTP 400"
    } as any);

    render(<Login />);
    fireEvent.change(screen.getByPlaceholderText(/you@example\.com/i), {
      target: { value: "x@y.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send magic link/i }));

    await waitFor(() => {
      expect(screen.getByText(/HTTP 400/i)).toBeInTheDocument();
    });
  });

  it('catch fallback shows "Something went wrong" when error has no message', async () => {
    // Reject with a plain object that lacks "message"
    vi.spyOn(g, "fetch").mockRejectedValueOnce({} as any);

    render(<Login />);
    fireEvent.change(screen.getByPlaceholderText(/you@example\.com/i), {
      target: { value: "z@z.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send magic link/i }));

    await waitFor(() => {
      expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    });
  });
});

