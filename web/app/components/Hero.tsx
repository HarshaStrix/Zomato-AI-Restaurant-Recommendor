'use client';

import Image from 'next/image';

const HERO_IMAGE =
  'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=80';

export default function Hero() {
  return (
    <section className="hero">
      <div className="heroBg">
        <Image
          src={HERO_IMAGE}
          alt="Restaurant dining"
          fill
          priority
          className="heroImg"
          sizes="100vw"
        />
        <div className="heroOverlay" />
      </div>
      <div className="heroContent">
        <h1 className="heroTitle">Zomato AI Restaurant Recommender</h1>
        <p className="heroSubtitle">
          Helping you find the best places to eat in Bangalore city
        </p>
      </div>
    </section>
  );
}
