'use client';

import { useState, useEffect, useCallback } from 'react';
import type { Options, Recommendation, Summary } from './types';
import AppHeader from './components/AppHeader';
import FilterForm from './components/FilterForm';
import RestaurantResults from './components/RestaurantResults';
import Footer from './components/Footer';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [options, setOptions] = useState<Options | null>(null);
  const [optionsError, setOptionsError] = useState<string | null>(null);
  const [location, setLocation] = useState('');
  const [cuisine, setCuisine] = useState('');
  const [priceTier, setPriceTier] = useState('');
  const [minRating, setMinRating] = useState('');
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[] | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const fetchOptions = useCallback(async () => {
    try {
      setOptionsError(null);
      const res = await fetch(`${API_URL}/api/v1/recommend/options`);
      if (!res.ok) throw new Error('Failed to load options');
      const data = await res.json();
      const locs = data.locations || [];
      const cuis = data.cuisines || [];
      const pr = data.price_ranges || [1, 2, 3, 4];
      const tiers = data.price_tiers || [];
      setOptions({ locations: locs, cuisines: cuis, price_ranges: pr, price_tiers: tiers });
    } catch (e) {
      setOptionsError(
        e instanceof Error ? e.message : 'Could not reach API. Is the server running at ' + API_URL + '?'
      );
    }
  }, []);

  useEffect(() => {
    fetchOptions();
  }, [fetchOptions]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const hasQuery = naturalLanguageQuery.trim().length > 0;
    const hasFilters = location?.trim() || cuisine?.trim() || priceTier || (minRating !== '' && minRating != null);
    if (!hasQuery && !hasFilters) {
      setSubmitError('Please select at least one filter (location, cuisine, price range, or min rating) or describe what you want.');
      setRecommendations(null);
      setSummary(null);
      return;
    }
    setLoading(true);
    setSubmitError(null);
    setRecommendations(null);
    setSummary(null);
    try {
      const body: Record<string, unknown> = { limit: 8 };
      const place = location?.trim();
      if (place) body.location = { place };
      if (cuisine) body.cuisine = cuisine;
      if (priceTier && ['budget', 'mid', 'premium'].includes(priceTier)) body.price_tier = priceTier;
      const ratingNum = minRating !== '' && minRating != null ? parseFloat(String(minRating)) : null;
      if (ratingNum != null && !Number.isNaN(ratingNum) && ratingNum >= 0 && ratingNum <= 5) {
        body.minimum_rating = Math.round(ratingNum * 10) / 10; // 0.1 precision
      }
      if (naturalLanguageQuery.trim()) body.natural_language_query = naturalLanguageQuery.trim();

      const res = await fetch(`${API_URL}/api/v1/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      let data: { data?: { recommendations?: unknown; summary?: unknown }; detail?: string; message?: string };
      try {
        data = await res.json();
      } catch {
        setSubmitError('Invalid response from server');
        return;
      }

      if (!res.ok) {
        const detail = (data as { detail?: string | { msg?: string }[] }).detail;
        const msg = Array.isArray(detail)
          ? detail.map((x) => (x && typeof x === 'object' && x.msg) || '').filter(Boolean).join(', ') || 'Request failed'
          : (detail ?? (data as { message?: string }).message ?? 'Request failed');
        setSubmitError(typeof msg === 'string' ? msg : 'Request failed');
        return;
      }

      const rawRecs = data?.data?.recommendations;
      const rawSummary = data?.data?.summary;
      setRecommendations(Array.isArray(rawRecs) ? rawRecs : []);
      setSummary(rawSummary && typeof rawSummary === 'object' && rawSummary !== null ? rawSummary as Summary : null);
    } catch (e) {
      setSubmitError(
        e instanceof Error ? e.message : 'Network error. Ensure the API is running at ' + API_URL
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="pageWrap">
      <AppHeader options={options} />

      <main className="container">
        <FilterForm
        options={options}
        optionsError={optionsError}
        location={location}
        setLocation={setLocation}
        cuisine={cuisine}
        setCuisine={setCuisine}
        priceTier={priceTier}
        setPriceTier={setPriceTier}
        minRating={minRating}
        setMinRating={setMinRating}
        naturalLanguageQuery={naturalLanguageQuery}
        setNaturalLanguageQuery={setNaturalLanguageQuery}
        onSubmit={handleSubmit}
        loading={loading}
      />

      {loading && (
        <div className="card">
          <div className="loading">
            <span className="spinner" />
            Fetching recommendations…
          </div>
        </div>
      )}

      {submitError && !loading && (
        <div className="card">
          <div className="error">{submitError}</div>
        </div>
      )}

      {recommendations !== null && !loading && (
        <RestaurantResults recommendations={recommendations} summary={summary} />
      )}

        <Footer />
      </main>
    </div>
  );
}
