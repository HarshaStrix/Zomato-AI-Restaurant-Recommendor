import type { Recommendation } from '../types';
import { IconLocation, IconCuisine, IconPrice, IconStar, IconReviews } from './Icons';

// Food/restaurant images by cuisine (Unsplash - use img for reliable loading)
const IMAGE_BY_CUISINE: Record<string, string> = {
  default:
    'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&q=80',
  'north indian':
    'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80',
  chinese: 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=400&q=80',
  italian: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80',
  cafe: 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&q=80',
  'south indian':
    'https://images.unsplash.com/photo-1631452180519-c014fe442f9a?w=400&q=80',
  mexican: 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400&q=80',
  continental:
    'https://images.unsplash.com/photo-1544025162-d76694265947?w=400&q=80',
  biryani: 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&q=80',
  american: 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=400&q=80',
  burger: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80',
  healthy: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80',
  salad: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=80',
};

function getImageForCuisine(cuisine: string): string {
  if (!cuisine) return IMAGE_BY_CUISINE.default;
  const parts = cuisine.toLowerCase().split(/[,\s]+/).map((p) => p.trim()).filter(Boolean);
  for (const part of parts) {
    if (IMAGE_BY_CUISINE[part]) return IMAGE_BY_CUISINE[part];
    if (part.includes('indian')) return IMAGE_BY_CUISINE['north indian'];
    if (part.includes('healthy')) return IMAGE_BY_CUISINE.healthy;
  }
  return IMAGE_BY_CUISINE.default;
}

type Props = { recommendation: Recommendation };

export default function RestaurantCard({ recommendation: rec }: Props) {
  const imgSrc = getImageForCuisine(rec.cuisine);

  return (
    <article className="restaurantCard">
      <div className="restaurantCardImageWrap">
        <img
          src={imgSrc}
          alt={rec.name}
          className="restaurantCardImage"
          loading="lazy"
        />
        <span className="restaurantCardRating"><IconStar size={14} /> {rec.rating}</span>
      </div>
      <div className="restaurantCardBody">
        <h3>{rec.name}</h3>
        <div className="restaurantMeta">
          <span><span className="metaIcon"><IconLocation size={14} /></span>{rec.location}</span>
          <span><span className="metaIcon"><IconCuisine size={14} /></span>{rec.cuisine}</span>
          {(rec.cost != null || rec.price_range != null) && (
            <span className="priceMeta">
              <span className="metaIcon"><IconPrice /></span>{rec.cost != null ? `${rec.cost} for two` : `${rec.price_range}/4`}
            </span>
          )}
          {rec.review_count != null && (
            <span><span className="metaIcon"><IconReviews size={14} /></span>{rec.review_count} reviews</span>
          )}
        </div>
        {rec.explanation && (
          <div className="explanation">{rec.explanation}</div>
        )}
      </div>
    </article>
  );
}
