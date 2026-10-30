import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import { LandingPage as StudioLandingPage } from '../studio_components/LandingPage';

/*
 * Tabs that live inside the Civic Navigator page. Anything in this set is
 * reached by navigating to /civic and telling that page which tab to open.
 *
 * The old handler was `else navigate('/dashboard')`, so the two tiles that
 * point at scheme_reader and form_filler dropped their tab and dumped the
 * visitor on the dashboard instead.
 */
const CIVIC_TAB_IDS = new Set([
  'navigator',
  'evidence',
  'action_plan',
  'scheme_reader',
  'bare_acts',
  'form_filler',
]);

export default function Landing() {
  const navigate = useNavigate();

  const handleStartQuery = (presetText) => {
    navigate('/civic', { state: { presetQuery: presetText } });
  };

  const handleExploreActs = () => {
    navigate('/civic', { state: { tab: 'bare_acts' } });
  };

  const handleNavigateToTab = (tab) => {
    if (tab === 'landing') {
      navigate('/');
    } else if (tab === 'drafter') {
      // The drafter is its own route, not a tab of /civic.
      navigate('/dochub');
    } else if (CIVIC_TAB_IDS.has(tab)) {
      navigate('/civic', { state: { tab } });
    } else {
      navigate('/civic');
    }
  };

  return (
    <div className="min-h-screen bg-paper text-ink flex flex-col font-sans">
      <Navbar />
      {/* Navbar is 64px, plus a ~46px nav strip below lg. */}
      <main className="flex-grow pt-[124px] lg:pt-[88px]">
        <StudioLandingPage
          onStartQuery={handleStartQuery}
          onExploreActs={handleExploreActs}
          onNavigateToTab={handleNavigateToTab}
        />
      </main>
      <Footer />
    </div>
  );
}
