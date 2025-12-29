interface NavigationProps {
  isConnected: boolean;
}

export function Navigation({ isConnected }: NavigationProps) {
  return (
    <header className="w-full bg-white/80 backdrop-blur-xl shadow-2xl border-b border-gray-200/50 sticky top-0 z-50">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-50/40 via-purple-50/30 to-pink-50/40 pointer-events-none" />

      <div
        className="relative max-w-7xl mx-auto py-8"
        style={{
          paddingLeft: '2rem',
          paddingRight: '2rem',
          paddingTop: '1rem'
        }}
      >
        <div className="flex items-center justify-between w-full">
          {/* Title block - Left */}
          <div className="flex flex-col">
            <h1
              className="text-[44px] md:text-[56px] lg:text-[64px] font-black tracking-tight"
              style={{
                backgroundImage:
                  "linear-gradient(135deg, #2563eb 0%, #7c3aed 50%, #ec4899 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                letterSpacing: "-0.03em",
              }}
            >
              FleetPulse
            </h1>
            <p className="text-xs text-gray-600 font-semibold tracking-wide uppercase mt-0.5">
              Real-time Fleet Monitoring
            </p>
          </div>
          {/* Badge - Right */}
          <div className="flex-shrink-0">
            {isConnected ? (
              <div className="relative group">
                {/* Glow effect */}
                <div className="absolute -inset-1 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full blur opacity-40 group-hover:opacity-60 transition-opacity" />

                {/* Badge */}
                <div className="relative flex gap-2.5 px-5 py-2.5 rounded-full bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg shadow-green-500/30 group-hover:shadow-xl group-hover:shadow-green-500/40 transition-all duration-300">
                  <div className="relative">
                    <span className="pulse-dot" />
                    <div className="absolute inset-0 bg-white rounded-full animate-ping opacity-75" />
                  </div>
                  <span className="font-bold text-sm tracking-wide">LIVE</span>
                </div>
              </div>
            ) : (
              <div className="relative group">
                <div className="flex gap-2.5 px-5 py-2.5 rounded-full bg-white shadow-lg border-2 border-red-200 group-hover:border-red-300 transition-colors">
                  <div className="relative">
                    <div className="h-2.5 w-2.5 rounded-full bg-red-500" />
                    <div className="absolute inset-0 h-2.5 w-2.5 rounded-full bg-red-500 animate-ping opacity-75" />
                  </div>
                  <span className="text-sm font-bold text-red-600">OFFLINE</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
