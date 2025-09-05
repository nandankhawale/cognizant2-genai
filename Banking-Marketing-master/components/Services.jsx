"use client";

export default function Services() {
  const services = [
    {
      icon: AccountsIcon,
      title: "Accounts",
      description: "Savings, Current, and specialized banking accounts tailored to your needs.",
      features: ["Savings", "Current"],
      link: "#accounts"
    },
    {
      icon: LoansIcon,
      title: "Loans",
      description: "AI-powered loan processing with instant eligibility check and competitive rates.",
      features: ["Personal", "Home", "Education", "Instant Approval"],
      link: "#loans"
    },
    {
      icon: CreditCardsIcon,
      title: "Credit Cards",
      description: "Premium credit cards with exclusive benefits, rewards, and cashback offers.",
      features: ["Premium Cards", "Rewards", "Cashback"],
      link: "#credit-cards"
    },
    {
      icon: InvestmentsIcon,
      title: "Investments",
      description: "Fixed Deposits, Recurring Deposits, and Mutual Funds for wealth creation.",
      features: ["FD", "RD", "Mutual Funds"],
      link: "#investments"
    },
    {
      icon: InsuranceIcon,
      title: "Insurance",
      description: "Life, Health, and General insurance products to protect what matters most.",
      features: ["Life", "Health", "General"],
      link: "#insurance"
    },
    {
      icon: DigitalBankingIcon,
      title: "Digital Banking",
      description: "Mobile banking, online services, and digital payment solutions.",
      features: ["Mobile Banking", "Online Services", "Digital Payments"],
      link: "#digital-banking"
    }
  ];

  return (
    <section className="py-16 lg:py-20 bg-white">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12 lg:mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            Our Services
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Comprehensive financial solutions designed to meet all your banking and investment needs
          </p>
        </div>

        {/* Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {services.map((service, index) => (
            <div
              key={index}
              className="group relative bg-[#000048] rounded-2xl p-6 lg:p-8 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 cursor-pointer"
            >
              {/* Icon */}
              <div className="mb-6">
                <service.icon className="h-12 w-12 text-white group-hover:text-[#1E90FF] transition-colors duration-300" />
              </div>

              {/* Content */}
              <div className="mb-6">
                <h3 className="text-xl lg:text-2xl font-bold text-white mb-3">
                  {service.title}
                </h3>
                <p className="text-white/90 text-sm lg:text-base leading-relaxed mb-4">
                  {service.description}
                </p>
                
                {/* Features */}
                <div className="flex flex-wrap gap-2">
                  {service.features.map((feature, featureIndex) => (
                    <span
                      key={featureIndex}
                      className="px-3 py-1 bg-white/10 rounded-full text-xs text-white/80 border border-white/20"
                    >
                      {feature}
                    </span>
                  ))}
                </div>
              </div>

              {/* CTA Link */}
              <div className="absolute bottom-6 left-6 right-6">
                <a
                  href={service.link}
                  className="inline-flex items-center text-[#1E90FF] font-semibold text-sm lg:text-base hover:text-white transition-colors duration-300 group-hover:translate-x-1"
                >
                  Know More
                  <svg
                    className="ml-2 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </a>
              </div>

              {/* Hover Effect Overlay */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-[#1E90FF]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-12 lg:mt-16">
          <p className="text-gray-600 mb-6">
            Need help choosing the right service for you?
          </p>
          <button className="inline-flex items-center gap-3 bg-[#000048] text-white px-8 py-4 rounded-xl font-semibold hover:bg-[#1E90FF] transition-colors duration-300 shadow-lg hover:shadow-xl">
            Get Expert Advice
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </button>
        </div>
      </div>
    </section>
  );
}

// Icon Components
function AccountsIcon({ className = "h-6 w-6" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 7l9-4 9 4-9 4-9-4z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 7v10l9 4 9-4V7" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v18" />
    </svg>
  );
}

function LoansIcon({ className = "h-6 w-6" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 12h18" />
    </svg>
  );
}

function CreditCardsIcon({ className = "h-6 w-6" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="5" width="20" height="14" rx="2" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M2 10h20" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 15h.01M10 15h.01" />
    </svg>
  );
}

function InvestmentsIcon({ className = "h-6 w-6" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 17l6-6 4 4 8-8" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 10V3h-7" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 3l-8 8" />
    </svg>
  );
}

function InsuranceIcon({ className = "h-6 w-6" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  );
}

function DigitalBankingIcon({ className = "h-6 w-6" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
      <line x1="8" y1="21" x2="16" y2="21" />
      <line x1="12" y1="17" x2="12" y2="21" />
      <circle cx="12" cy="10" r="2" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h8" />
    </svg>
  );
}
