import type { Recommendation, Summary } from '../types';
import AISummary from './AISummary';
import RestaurantCard from './RestaurantCard';

type Props = {
  recommendations: Recommendation[];
  summary: Summary | null;
};

export default function RestaurantResults({ recommendations, summary }: Props) {
  const list = Array.isArray(recommendations) ? recommendations.filter((rec) => rec && typeof rec === 'object') : [];
  return (
    <div className="card resultsSection">
      {summary && typeof summary === 'object' && summary !== null && <AISummary summary={summary as Summary} />}
      {list.length === 0 ? (
        <div className="noResults">No restaurants match your filters. Try different options.</div>
      ) : (
        list.map((rec, index) => (
          <RestaurantCard
            key={rec.restaurant_id ? `id-${rec.restaurant_id}` : `idx-${index}`}
            recommendation={rec as Recommendation}
          />
        ))
      )}
    </div>
  );
}
