import { IconSpark } from './Icons';
import type { Options } from '../types';

type AppHeaderProps = {
  options?: Options | null;
};

export default function AppHeader({ options }: AppHeaderProps) {
  const locationCount = options?.locations?.length ?? 0;
  const cuisineCount = options?.cuisines?.length ?? 0;

  return (
    <header className="appHeader">
      <h1 className="appHeaderTitle">
        <span className="appHeaderTitleIcon" aria-hidden>
          <IconSpark size={22} />
        </span>
        Zomato AI Restaurant Recommender
      </h1>
      <p className="appHeaderSubtitle">
        Helping you find the best places to eat in{' '}
        <span className="highlightBangalore">Bangalore</span> city
      </p>
      {(locationCount > 0 || cuisineCount > 0) && (
        <div className="statsCapsule" aria-label="Dataset statistics">
          <span className="statsCapsuleItem">
            <svg className="statsIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
            {locationCount} locations
          </span>
          <span className="statsCapsuleDivider" aria-hidden>•</span>
          <span className="statsCapsuleItem">
            <svg className="statsIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
              <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2" />
              <path d="M7 2v20" />
              <path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7" />
            </svg>
            {cuisineCount} cuisines
          </span>
        </div>
      )}
    </header>
  );
}
