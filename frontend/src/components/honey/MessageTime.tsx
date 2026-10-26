export function timeLabels(timestamp: number | null | undefined, timezone: string) {
  if (typeof timestamp !== "number" || !Number.isFinite(timestamp) || timestamp <= 0) return null;
  const date = new Date(timestamp * 1000);
  if (!Number.isFinite(date.getTime())) return null;
  try {
    const day = new Intl.DateTimeFormat("zh-CN", { timeZone: timezone, year: "numeric", month: "2-digit", day: "2-digit" }).format(date);
    const clock = new Intl.DateTimeFormat("zh-CN", { timeZone: timezone, hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(date);
    return { day, clock, iso: date.toISOString() };
  } catch { return null; }
}

export function MessageTime({ timestamp, timezone }: { timestamp?: number | null; timezone: string }) {
  const labels = timeLabels(timestamp, timezone);
  return labels ? <time dateTime={labels.iso} title={`${labels.day} ${labels.clock} · ${timezone}`} className="mt-1 block text-[11px] text-[var(--foreground-faint)]">{labels.clock}</time> : null;
}
