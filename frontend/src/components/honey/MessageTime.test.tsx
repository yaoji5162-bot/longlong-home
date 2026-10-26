import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MessageTime, timeLabels } from "./MessageTime";

describe("message time", () => {
  it("uses configured timezone across midnight", () => {
    const timestamp = Date.parse("2026-10-25T16:10:00Z") / 1000;
    expect(timeLabels(timestamp, "Asia/Shanghai")).toMatchObject({ day: "2026/10/26", clock: "00:10" });
    expect(timeLabels(timestamp, "UTC")).toMatchObject({ day: "2026/10/25", clock: "16:10" });
    render(<MessageTime timestamp={timestamp} timezone="Asia/Shanghai" />);
    expect(screen.getByText("00:10").getAttribute("datetime")).toBe("2026-10-25T16:10:00.000Z");
  });
  it("never invents dates for old or malformed messages", () => {
    for (const value of [null, undefined, NaN, Infinity, -1]) expect(timeLabels(value, "Asia/Shanghai")).toBeNull();
    const { container } = render(<MessageTime timezone="Asia/Shanghai" />);
    expect(container.querySelector("time")).toBeNull();
  });
});
