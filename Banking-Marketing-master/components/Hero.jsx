"use client";

import { useState, useEffect } from 'react';

export default function Hero() {
  const [currentSlide, setCurrentSlide] = useState(0);
  
  const slides = [
    {
      image: '/assets/banking.jpg',
      title: 'Professional Banking Services',
      subtitle: 'Experience world-class financial solutions'
    },
    {
      image: '/assets/home.jpg', 
      title: 'Your Dream Home Awaits',
      subtitle: 'Get the best home loan rates with us'
    },
    {
    image: '/assets/car.jpg', 
    title: 'Drive Your Dream Car',
    subtitle: 'Get affordable car loan rates tailored for you'
    },
    {
      image: '/assets/home.jpg', 
      title: 'Your Dream Home Awaits',
      subtitle: 'Easy, fast & reliable home loan solutions.'
    }

  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 4000); // Change slide every 4 seconds

    return () => clearInterval(timer);
  }, [slides.length]);
  return (
    <section className="relative w-full bg-[#000049]" style={{ height: 'calc(100svh - var(--header-h, 80px))' }}>
      {/* Background */}
      <div className="relative overflow-hidden h-full w-full">
        <div className="relative text-white h-full flex flex-col">
          {/* Soft gradient overlays for depth */}
          <div className="pointer-events-none absolute inset-0 opacity-15" style={{background: "radial-gradient(1200px 500px at 80% 0%, rgba(255,255,255,0.25) 0%, transparent 60%)"}} />

          <div className="relative mx-auto max-w-7xl px-6 lg:px-8 grid grid-cols-1 lg:grid-cols-2 gap-8 py-6 lg:py-8 h-full flex-1 items-center">
            {/* Left column */}
            <div className="flex flex-col gap-6">
              {/* Top Banner/Slogan */}
              <div className="space-y-2">
                <h2 className="text-3xl sm:text-4xl lg:text-4xl font-bold leading-tight text-white">
                  Truth, Trust, Transparency
                </h2>
                <p className="text-base text-white/90 max-w-md">
                  Your trusted banking partner for all financial needs
                </p>
              </div>

              {/* Search Bar */}
              <div className="w-full max-w-xl">
                <label htmlFor="global-search" className="sr-only">Search</label>
                <div className="flex items-center gap-3 rounded-xl bg-white/95 shadow-md ring-1 ring-white/60 focus-within:ring-2 focus-within:ring-white/80 px-4 py-2.5">
                  {/* Magnifying Glass Icon */}
                  <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-4.35-4.35M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15z" />
                  </svg>
                  <input
                    id="global-search"
                    type="text"
                    placeholder={'Search for "Savings Account"'}
                    className="flex-1 bg-transparent text-sm sm:text-base text-gray-900 placeholder-gray-500 focus:outline-none"
                  />
                  {/* Microphone Icon */}
                  <button aria-label="voice search" className="shrink-0 rounded-md p-1.5 hover:bg-gray-100/70 transition">
                    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3a3 3 0 0 0-3 3v6a3 3 0 1 0 6 0V6a3 3 0 0 0-3-3z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 10v1a7 7 0 0 1-14 0v-1M12 21v-2" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Quick Access Navigation */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white">Quick Access</h3>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: "Accounts", icon: AccountsIcon },
                    { label: "Cards", icon: CardsIcon },
                    { label: "Loans", icon: LoansIcon },
                    { label: "Deposits", icon: DepositsIcon },
                    { label: "Investment", icon: InvestmentIcon },
                    { label: "Get Support", sub: "1800 1080", icon: SupportIcon },
                  ].map((item) => (
                    <button
                      key={item.label}
                      className="group flex flex-col items-center justify-center rounded-xl bg-white/95 px-4 py-4 shadow-md ring-1 ring-white/70 hover:shadow-lg transition text-center"
                    >
                      <item.icon className="h-6 w-6 mb-1.5" />
                      <span className="text-sm font-semibold" style={{color: "#000049"}}>{item.label}</span>
                      {item.sub && (
                        <span className="mt-0.5 text-xs text-gray-600">{item.sub}</span>
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* Pick Where You Left */}
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-white">Pick where you left</h3>
                <div className="flex items-center justify-between gap-4 rounded-xl bg-white/95 p-4 shadow-md ring-1 ring-white/70">
                  <div className="flex-1">
                    <p className="text-sm font-semibold mb-1" style={{color: "#000049"}}>Need a loan? Get instant eligibility!</p>
                    <div className="flex items-center gap-4 text-xs font-bold" style={{color: "#000049"}}>
                      <button className="hover:underline" onClick={() => document.querySelector('[data-chatbot-button]')?.click()}>APPLY NOW</button>
                      <a href="#loans" className="hover:underline">KNOW MORE</a>
                    </div>
                  </div>
                  {/* Small related image placeholder */}
                  <div className="shrink-0 w-14 h-14 rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 ring-1 ring-white/70 flex items-center justify-center">
                    <svg className="h-7 w-7" style={{color: "#000049"}} viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Right column - Slideshow and Featured Promotion */}
            <div className="relative flex flex-col gap-4">
              {/* Image Slideshow */}
              <div className="relative w-full h-[200px] rounded-2xl overflow-hidden shadow-xl ring-1 ring-white/60">
                <div className="relative h-full w-full">
                  {slides.map((slide, index) => (
                    <div
                      key={index}
                      className={`absolute inset-0 transition-opacity duration-1000 ${
                        index === currentSlide ? 'opacity-100' : 'opacity-0'
                      }`}
                    >
                      <div 
                        className="absolute inset-0 bg-cover bg-center"
                        style={{backgroundImage: `url('${slide.image}')`}}
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                      <div className="absolute bottom-4 left-4 right-4">
                        <h4 className="text-lg font-bold text-white mb-1">{slide.title}</h4>
                        <p className="text-sm text-white/90">{slide.subtitle}</p>
                      </div>
                    </div>
                  ))}
                  
                  {/* Slide indicators */}
                  <div className="absolute top-4 right-4 flex gap-2">
                    {slides.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentSlide(index)}
                        className={`w-2 h-2 rounded-full transition-all duration-300 ${
                          index === currentSlide ? 'bg-white' : 'bg-white/50'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>

              {/* Featured Promotion */}
              <div className="relative w-full h-[200px] rounded-2xl overflow-hidden shadow-xl ring-1 ring-white/60">
                {/* Background image placeholder with soft mask */}
                <div className="absolute inset-0 bg-cover bg-center"  />
                {/* Fallback gradient if image missing */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#000049]/80 to-[#000049]/60" />

                <div className="relative h-full w-full p-4 lg:p-6 flex flex-col justify-end">
                  <div className="max-w-sm">
                    <h3 className="text-xl lg:text-2xl font-bold text-white mb-2">CLIENT CONNECT - Feedback Day</h3>
                    <p className="text-sm text-white/90 mb-3">
                      Share feedback & resolve queries, every 2nd Tuesday
                    </p>
                    <div>
                      <button className="inline-flex items-center gap-2 rounded-lg bg-white/95 px-4 py-2 text-sm font-bold shadow-md ring-1 ring-white/80 hover:bg-white transition" style={{color: "#000049"}}>
                        Locate Us
                        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Banner (temporarily hidden to ensure no scroll) */}
          <div className="hidden">
            <div className="mx-auto max-w-7xl px-8 lg:px-12 pb-8">
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                {[
                  { label: 'Service Request', icon: ServiceIcon },
                  { label: 'Track Applications', icon: TrackIcon },
                  { label: 'Smart Lock', icon: LockIcon },
                  { label: 'Block Card', icon: BlockIcon },
                  { label: 'Report Fraud', icon: FraudIcon },
                  { label: 'Help', icon: HelpIcon },
                ].map((item) => (
                  <a key={item.label} href="#" className="flex items-center gap-3 rounded-xl bg-white/95 px-5 py-4 shadow-lg ring-1 ring-white/70 hover:shadow-xl hover:scale-105 transition-all duration-200">
                    <item.icon className="h-6 w-6" />
                    <span className="text-sm font-semibold" style={{color: "#000049"}}>{item.label}</span>
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function AccountsIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7l9-4 9 4-9 4-9-4z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v10l9 4 9-4V7" />
    </svg>
  );
}
function CardsIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <rect x="2" y="5" width="20" height="14" rx="2" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2 10h20" />
    </svg>
  );
}
function LoansIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12h18M7 12v6m10-6v6M5 9h14l-2-4H7l-2 4z" />
    </svg>
  );
}
function DepositsIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3l9 6-9 6-9-6 9-6z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 13l9 6 9-6" />
    </svg>
  );
}
function InvestmentIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 17l6-6 4 4 7-7" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 10V3h-7" />
    </svg>
  );
}
function SupportIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <circle cx="12" cy="12" r="9" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 15s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" />
    </svg>
  );
}

function ServiceIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6M4 6h16M4 18h16" />
    </svg>
  );
}
function TrackIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <circle cx="12" cy="12" r="9" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 7v5l3 3" />
    </svg>
  );
}
function LockIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 11V8a3 3 0 1 1 6 0v3" />
    </svg>
  );
}
function BlockIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <circle cx="12" cy="12" r="9" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 8l8 8" />
    </svg>
  );
}
function FraudIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 2l9 4-9 4-9-4 9-4z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10l9 4 9-4M3 14l9 4 9-4" />
    </svg>
  );
}
function HelpIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{color: "#000049"}}>
      <circle cx="12" cy="12" r="9" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.09 9a3 3 0 1 1 5.82 1c0 2-3 2-3 4" />
      <circle cx="12" cy="17" r=".5" />
    </svg>
  );
}
