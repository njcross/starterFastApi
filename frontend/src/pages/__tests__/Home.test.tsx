import { render, screen, fireEvent } from "@testing-library/react";
import Home from "../Home";

// Mock fetch so tests don't call the real API
global.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: async () => ({ ok: true }),
}) as any;

describe("Home Page", () => {
  it("renders buttons", () => {
    render(<Home />);
    expect(screen.getByText(/Five Eyes Cyber Hygiene/i)).toBeInTheDocument();
    expect(screen.getByText(/Health/i)).toBeInTheDocument();
    expect(screen.getByText(/Ping Redis/i)).toBeInTheDocument();
    expect(screen.getByText(/DB Version/i)).toBeInTheDocument();
  });

  it("calls health and shows a log line", async () => {
    render(<Home />);
    fireEvent.click(screen.getByText(/Health/i));
    const item = await screen.findByText(/health/i);
    expect(item).toBeInTheDocument();
  });
});
