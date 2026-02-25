/** Subtle, neat SVG icons – Zomato-style */

type IconProps = { className?: string; size?: number };

const s = (size: number = 18) => size;

export function IconLocation({ className, size = 18 }: IconProps) {
  const d = s(size);
  return (
    <svg className={className} width={d} height={d} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  );
}

export function IconCuisine({ className, size = 18 }: IconProps) {
  const d = s(size);
  return (
    <svg className={className} width={d} height={d} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2" />
      <path d="M7 2v20" />
      <path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7" />
    </svg>
  );
}

/** Indian Rupee (₹) - text-based for perfect alignment and size matching */
export function IconPrice({ className }: IconProps) {
  return (
    <span className={className} style={{ fontWeight: 600, fontStyle: 'normal' }}>₹</span>
  );
}

export function IconStar({ className, size = 18 }: IconProps) {
  const d = s(size);
  return (
    <svg className={className} width={d} height={d} viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
    </svg>
  );
}

export function IconReviews({ className, size = 18 }: IconProps) {
  const d = s(size);
  return (
    <svg className={className} width={d} height={d} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

export function IconSearch({ className, size = 20 }: IconProps) {
  const d = s(size);
  return (
    <svg className={className} width={d} height={d} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  );
}

export function IconSpark({ className, size = 20 }: IconProps) {
  const d = s(size);
  return (
    <svg className={className} width={d} height={d} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
    </svg>
  );
}
