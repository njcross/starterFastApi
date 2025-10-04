// src/__tests__/main.render.test.ts
import { vi, describe, it, expect, beforeEach } from "vitest";

// mock react-dom/client so we can spy on createRoot
vi.mock("react-dom/client", async () => {
  const actual = await vi.importActual<any>("react-dom/client");
  return {
    ...actual,
    createRoot: vi.fn(() => ({
      render: vi.fn(),
    })),
  };
});

describe("main.tsx bootstraps React root", async () => {
  beforeEach(() => {
    // ensure a fresh root element and clear module cache
    document.body.innerHTML = `<div id="root"></div>`;
    vi.resetModules();
  });

  it("calls createRoot and render", async () => {
    const { createRoot } = await import("react-dom/client");
    const mod = await import("../main"); // importing runs the code

    // not really using `mod`, import triggers side effects
    expect(createRoot).toHaveBeenCalledTimes(1);
    const arg = (createRoot as any).mock.calls[0][0];
    expect(arg).toBeInstanceOf(HTMLElement);

    // grab the returned object’s render function
    const ret = (createRoot as any).mock.results[0].value;
    expect(ret.render).toHaveBeenCalledTimes(1);
  });
});
