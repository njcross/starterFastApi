import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Login from "./Login";

describe("Login page (magic link)", () => {
  beforeEach(() => {
    (global.fetch as any) = vi.fn();
  });

  it("submits email and shows success message", async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ sent: true }),
    });

    render(<Login />);
    const input = screen.getByPlaceholderText(/you@example.com/i);
    await userEvent.type(input, "person@example.com");

    const btn = screen.getByRole("button", { name: /send magic link/i });
    await userEvent.click(btn);

    expect(await screen.findByText(/we’ve sent a sign-in link/i)).toBeInTheDocument();
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/auth/request-link",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
    );
  });

  it("shows error message when API fails", async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ error: "bad email" }),
    });

    render(<Login />);
    const input = screen.getByPlaceholderText(/you@example.com/i);
    await userEvent.type(input, "broken@example.com");
    await userEvent.click(screen.getByRole("button", { name: /send magic link/i }));

    expect(await screen.findByText(/bad email/i)).toBeInTheDocument();
  });
});
