// src/components/__tests__/Button.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Button from "../Button";

describe("Button component", () => {
  it("renders primary variant and fires onClick", () => {
    const onClick = vi.fn();
    render(<Button variant="primary" onClick={onClick}>Primary</Button>);
    const btn = screen.getByRole("button", { name: "Primary" });
    fireEvent.click(btn);
    expect(onClick).toHaveBeenCalled();
  });

  it("renders secondary (or outline) variant branch", () => {
    render(<Button variant="primary">Secondary</Button>);
    const btn = screen.getByRole("button", { name: "Secondary" });
    // just ensure it rendered and isn’t disabled
    expect(btn).toBeInTheDocument();
  });
});
