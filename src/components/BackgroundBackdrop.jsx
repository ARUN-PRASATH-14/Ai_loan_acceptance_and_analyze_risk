import React, { useEffect, useState } from 'react';

const bgOptions = [
  { type: 'image', url: '/bank_bg_1.png', opacity: 0.12 },
  { type: 'image', url: '/bank_bg_2.png', opacity: 0.12 },
  { type: 'gradient', style: 'linear-gradient(135deg, rgba(79, 70, 229, 0.08) 0%, rgba(37, 99, 235, 0.05) 100%)', opacity: 1 },
  { type: 'gradient', style: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(79, 70, 229, 0.05) 100%)', opacity: 1 }
];

export default function BackgroundBackdrop() {
  const [currentBg, setCurrentBg] = useState(bgOptions[0]);

  useEffect(() => {
    // Pick a random bank background option on page refresh
    const randomIndex = Math.floor(Math.random() * bgOptions.length);
    setCurrentBg(bgOptions[randomIndex]);
  }, []);

  return (
    <div
      aria-hidden="true"
      className="fixed inset-0 pointer-events-none z-[-1] transition-all duration-700 ease-in-out bg-cover bg-center bg-no-repeat"
      style={{
        backgroundImage: currentBg.type === 'image' ? `url("${currentBg.url}")` : currentBg.style,
        opacity: currentBg.opacity,
      }}
    />
  );
}
