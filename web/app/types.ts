export type PriceTierOption = { value: string; label: string };

export type Options = {
  locations: string[];
  cuisines: string[];
  price_ranges: number[];
  price_tiers?: PriceTierOption[];
};

export type Recommendation = {
  restaurant_id: number;
  name: string;
  location: string;
  cuisine: string;
  rating: number;
  price_range: number | null;
  cost: number | null;  // Cost for two in ₹ (Indian Rupees)
  review_count: number | null;
  score: number;
  explanation: string | null;
};

export type Summary = {
  total_found: number;
  returned: number;
  ai_explanation: string | null;
};

export const PRICE_TIER_OPTIONS = [
  { value: '', label: 'Any' },
  { value: 'budget', label: 'Budget friendly (≤ ₹500)' },
  { value: 'mid', label: 'Mid-range (₹500–₹1500)' },
  { value: 'premium', label: 'Premium (> ₹1500)' },
] as const;

