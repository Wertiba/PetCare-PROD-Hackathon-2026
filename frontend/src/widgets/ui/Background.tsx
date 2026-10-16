interface BackgroundProps {
  className?: string;
}

/**
 * Neutral app background. Previously an animated simplex-noise canvas —
 * reduced to a plain white layer for the minimal baseline.
 */
export function Background({ className }: BackgroundProps) {
  return (
    <div
      id="app-background"
      aria-hidden="true"
      className={`pointer-events-none fixed inset-0 -z-10 h-full w-full bg-white ${className ?? ''}`}
    />
  );
}
