import { render, screen, fireEvent } from "@testing-library/react";
import App from "./App";

// Mock fetch so tests don't call the real API
global.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: async () => ({ ok: true }),
}) as any;

describe("App", () => {
  it("renders and shows buttons", () => {
    render(<App />);
    expect(screen.getByText(/Five Eyes Cyber Hygiene/i)).toBeInTheDocument();
    expect(screen.getByText(/Health/i)).toBeInTheDocument();
    expect(screen.getByText(/Ping Redis/i)).toBeInTheDocument();
    expect(screen.getByText(/DB Version/i)).toBeInTheDocument();
  });

  it("calls health and logs a result", async () => {
    render(<App />);
    const btn = screen.getByText(/Health/i);
    fireEvent.click(btn);
    const item = await screen.findByText(/health/i);
    expect(item).toBeInTheDocument();
  });
});
