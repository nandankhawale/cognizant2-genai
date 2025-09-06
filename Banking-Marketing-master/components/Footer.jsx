"use client";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const quickLinks = [
    { name: "Home", href: "#home" },
    { name: "Personal Banking", href: "#personal-banking" },
    { name: "Loans", href: "#loans" },
    { name: "Credit Cards", href: "#credit-cards" },
    { name: "Investments", href: "#investments" },
    { name: "Insurance", href: "#insurance" },
    { name: "About", href: "#about" },
    { name: "Contact Us", href: "#contact" },
    { name: "Admin", href: "/admin" }
  ];

  const socialLinks = [
    {
      name: "LinkedIn",
      href: "#linkedin",
      icon: LinkedInIcon
    },
    {
      name: "Twitter", 
      href: "#twitter",
      icon: TwitterIcon
    },
    {
      name: "YouTube",
      href: "#youtube", 
      icon: YouTubeIcon
    }
  ];

  return (
    <footer className="bg-[#000048] text-white">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-12 lg:py-16">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
          
          {/* Left Side - Logo & Tagline */}
          <div className="text-center md:text-left">
            <div className="mb-4">
              <h3 className="text-2xl lg:text-3xl font-bold">
                <span className="text-white">Cogni</span>
                <span className="text-[#1E90FF]">Bank</span>
              </h3>
            </div>
            <p className="text-white/80 text-sm lg:text-base leading-relaxed max-w-sm mx-auto md:mx-0">
              NextBank – Banking Made Simple. Your trusted partner for all financial needs.
            </p>
          </div>

          {/* Center - Quick Navigation Links */}
          <div className="text-center md:text-left">
            <h4 className="text-lg font-semibold mb-6 text-white">Quick Links</h4>
            <div className="grid grid-cols-2 gap-3">
              {quickLinks.map((link, index) => (
                <a
                  key={index}
                  href={link.href}
                  className="text-white/80 hover:text-[#1E90FF] transition-colors duration-300 text-sm lg:text-base"
                >
                  {link.name}
                </a>
              ))}
            </div>
          </div>

          {/* Right Side - Social Media */}
          <div className="text-center md:text-left">
            <h4 className="text-lg font-semibold mb-6 text-white">Follow Us</h4>
            <div className="flex justify-center md:justify-start gap-4">
              {socialLinks.map((social, index) => (
                <a
                  key={index}
                  href={social.href}
                  className="group p-3 rounded-full bg-white/10 hover:bg-[#1E90FF] transition-all duration-300"
                  aria-label={social.name}
                >
                  <social.icon className="h-5 w-5 text-white group-hover:text-white transition-colors duration-300" />
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 lg:mt-16 pt-8 border-t border-white/20">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            {/* Copyright */}
            <div className="text-center md:text-left">
              <p className="text-white/70 text-sm">
                © {currentYear} NextBank. All Rights Reserved.
              </p>
            </div>
            
            {/* Disclaimer */}
            <div className="text-center md:text-right">
              <p className="text-white/60 text-xs lg:text-sm">
                This is a demo banking website for hackathon purposes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

// Social Media Icon Components
function LinkedInIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
    </svg>
  );
}

function TwitterIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
    </svg>
  );
}

function YouTubeIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
    </svg>
  );
}
