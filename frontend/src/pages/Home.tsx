/**
 * Home Page Component
 * Displays the Hero section
 */

import { Hero } from '../components/sections/Hero';

export function Home() {
  return (
    <Hero 
      title="Welcome to Neo Alexandria" 
      subtitle="Your personal knowledge management system with beautiful dual-theme design"
      backgroundAnimation={true}
    />
  );
}
