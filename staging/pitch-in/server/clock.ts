// A clock with a demo offset, so the video can show "7 days later" without waiting.
// The offset is recorded in the ledger every time it changes.

let offsetMs = 0;

export const clock = {
  now(): Date {
    return new Date(Date.now() + offsetMs);
  },
  iso(): string {
    return this.now().toISOString();
  },
  advance(days: number) {
    offsetMs += days * 86_400_000;
  },
  offsetDays(): number {
    return offsetMs / 86_400_000;
  },
  reset() {
    offsetMs = 0;
  },
};

export const DAY_MS = 86_400_000;

export function daysBetween(fromIso: string, to: Date): number {
  return (new Date(fromIso).getTime() - to.getTime()) / DAY_MS;
}
