'use client';

import { PRICE_TIER_OPTIONS } from '../types';
import type { Options } from '../types';
import ApiHint from './ApiHint';
import { IconLocation, IconCuisine, IconPrice, IconStar, IconSearch } from './Icons';

const MIN_RATING_BUTTON_STEP = 0.5;  // (-) and (+) buttons
const MIN_RATING_ARROW_STEP = 0.1;   // up/down arrow keys
const MIN_RATING_MIN = 0;
const MIN_RATING_MAX = 5;

type FilterFormProps = {
  options: Options | null;
  optionsError: string | null;
  location: string;
  setLocation: (v: string) => void;
  cuisine: string;
  setCuisine: (v: string) => void;
  priceTier: string;
  setPriceTier: (v: string) => void;
  minRating: string;
  setMinRating: (v: string) => void;
  naturalLanguageQuery: string;
  setNaturalLanguageQuery: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
};

export default function FilterForm({
  options,
  optionsError,
  location,
  setLocation,
  cuisine,
  setCuisine,
  priceTier,
  setPriceTier,
  minRating,
  setMinRating,
  naturalLanguageQuery,
  setNaturalLanguageQuery,
  onSubmit,
  loading,
}: FilterFormProps) {
  const ratingNum = minRating === '' ? null : parseFloat(minRating);
  const handleRatingDelta = (delta: number, useButtonStep: boolean) => {
    const step = useButtonStep ? MIN_RATING_BUTTON_STEP : MIN_RATING_ARROW_STEP;
    const current = ratingNum ?? 0;
    const next = Math.round((current + delta) / step) * step;
    const clamped = Math.max(MIN_RATING_MIN, Math.min(MIN_RATING_MAX, next));
    const formatted = clamped % 1 === 0 ? String(clamped) : clamped.toFixed(1);
    setMinRating(formatted);
  };

  return (
    <div className="card cardSearch">
      {optionsError && <ApiHint message={optionsError} />}
      <form onSubmit={onSubmit}>
        <div className="formGrid">
          <div>
            <label className="label" htmlFor="location">
              <span className="labelIcon"><IconLocation size={16} /></span> Location
            </label>
            <select
              id="location"
              className="select"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              disabled={!options}
            >
              <option value="">{options ? 'Any' : 'Loading…'}</option>
              {options?.locations.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="cuisine">
              <span className="labelIcon"><IconCuisine size={16} /></span> Cuisine
            </label>
            <select
              id="cuisine"
              className="select"
              value={cuisine}
              onChange={(e) => setCuisine(e.target.value)}
            >
              <option value="">Any</option>
              {options?.cuisines.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="priceTier">
              <span className="labelIcon"><IconPrice size={16} /></span> Price range
            </label>
            <select
              id="priceTier"
              className="select"
              value={priceTier}
              onChange={(e) => setPriceTier(e.target.value)}
            >
              {PRICE_TIER_OPTIONS.map((opt) => (
                <option key={opt.value || 'any'} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="minRating">
              <span className="labelIcon"><IconStar size={16} /></span> Min rating
            </label>
            <div className="ratingInputWrap">
              <button
                type="button"
                className="ratingBtn"
                onClick={() => handleRatingDelta(-0.5, true)}
                aria-label="Decrease rating by 0.5"
              >
                −
              </button>
              <input
                id="minRating"
                type="number"
                className="input ratingInput"
                min={MIN_RATING_MIN}
                max={MIN_RATING_MAX}
                step={MIN_RATING_ARROW_STEP}
                placeholder="Any"
                value={minRating}
                onChange={(e) => setMinRating(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    handleRatingDelta(0.1, false);
                  } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    handleRatingDelta(-0.1, false);
                  }
                }}
              />
              <button
                type="button"
                className="ratingBtn"
                onClick={() => handleRatingDelta(0.5, true)}
                aria-label="Increase rating by 0.5"
              >
                +
              </button>
            </div>
          </div>
        </div>
        <div className="formFieldFull">
          <label className="label" htmlFor="naturalLanguageQuery">
            <span className="labelIcon"><IconSearch size={16} /></span> Or describe what you want
          </label>
          <input
            id="naturalLanguageQuery"
            type="text"
            className="input"
            placeholder="e.g. Romantic place for dinner under ₹1500"
            value={naturalLanguageQuery}
            onChange={(e) => setNaturalLanguageQuery(e.target.value)}
            maxLength={500}
          />
          <span className="fieldHint">
            Use the 4 dropdowns above, or only this box — AI will understand and recommend.
          </span>
        </div>
        <button type="submit" className="btn" disabled={loading || !options}>
          {loading ? 'Finding…' : 'Find restaurants'}
        </button>
      </form>
    </div>
  );
}
