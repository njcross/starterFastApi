// src/pages/__tests__/About.test.tsx
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import About from "../About";

describe("About page", () => {
  it("renders", () => {
    render(<About />);
    // adapt to your actual headings/text
    expect(screen.getByText(/about/i)).toBeInTheDocument();
  });
});
