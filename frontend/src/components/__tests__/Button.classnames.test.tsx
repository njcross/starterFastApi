// src/components/__tests__/Button.classnames.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Button from "../Button";

describe("Button className variants", () => {
  it('uses "btn-primary" by default and appends custom className', () => {
    const onClick = vi.fn();
    render(
      <Button className="extra" onClick={onClick}>
        Default
      </Button>
    );
    const btn = screen.getByRole("button", { name: "Default" });
    expect(btn.className).toMatch(/\bbtn\b/);
    expect(btn.className).toMatch(/\bbtn-primary\b/); // default branch
    expect(btn.className).toMatch(/\bextra\b/);       // props.className ?? ""
    fireEvent.click(btn);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('uses "btn-ghost" when variant="ghost"', () => {
    render(<Button variant="ghost">Ghost</Button>);
    const btn = screen.getByRole("button", { name: "Ghost" });
    expect(btn.className).toMatch(/\bbtn\b/);
    expect(btn.className).toMatch(/\bbtn-ghost\b/);   // ghost branch
    expect(btn.className).not.toMatch(/\bbtn-primary\b/);
  });
});
