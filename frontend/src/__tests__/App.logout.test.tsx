// frontend/src/App.logout.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import App from "../App";
import { vi } from "vitest";
import * as UserContext from "../contexts/UserContext";

// Mock fetch so tests don't hit the real API
global.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: async () => ({ ok: true }),
}) as any;

describe("App navigation and logout", () => {
  it("renders Logout when user is logged in and calls logout", async () => {
    const logout = vi.fn();

    // Mock useUser to simulate a logged-in user
    vi.spyOn(UserContext, "useUser").mockReturnValue({
      currentUser: { id: 1, email: "test@example.com" },
      logout,
    });

    render(<App />);

    // The nav should show welcome + logout
    expect(screen.getByText(/Welcome, test@example.com/i)).toBeInTheDocument();
    const btn = screen.getByText(/Logout/i);
    fireEvent.click(btn);
    expect(logout).toHaveBeenCalledTimes(1);

    // Clean up mocks
    vi.restoreAllMocks();
  });
});
