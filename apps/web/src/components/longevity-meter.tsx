export function LongevityMeter({ score, compact = false }: { score: number; compact?: boolean }) {
  const value = Math.max(0, Math.min(100, Math.round(score)));
  return (
    <div className={`longevity-meter${compact ? " is-compact" : ""}`}>
      <div className="longevity-meter-heading">
        <span>AD LONGEVITY SCORE</span>
        <strong>{value}<small>/100</small></strong>
      </div>
      <div
        className="longevity-meter-track"
        role="meter"
        aria-label="Ad Longevity Score"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={value}
      >
        <span className="longevity-meter-fill" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
