import React from "react";

interface SaarthiLogoProps {
  size?: number;
  className?: string;
  showText?: boolean;
  textClassName?: string;
  subtitleClassName?: string;
}

export const SaarthiLogo: React.FC<SaarthiLogoProps> = ({
  size = 36,
  className = "",
  showText = true,
  textClassName = "",
  subtitleClassName = "",
}) => {
  return (
    <div className={`inline-flex items-center gap-3 ${className}`}>
      {/* Official Saarthi Logo Symbol */}
      <img
        src="/saarthi-logo.png"
        alt="Saarthi — YOUR AI COMPANION"
        className="shrink-0 rounded-lg object-contain shadow-[0_0_15px_rgba(245,158,11,0.2)] transition-transform hover:scale-105"
        style={{ width: size, height: size }}
      />

      {showText && (
        <div className="flex flex-col">
          <span
            className={`font-bold tracking-wider text-white text-base font-sans ${textClassName}`}
            style={{ fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif" }}
          >
            Saarthi
          </span>
          <span
            className={`text-[9px] tracking-[0.2em] text-[#F59E0B] uppercase font-mono -mt-0.5 font-semibold ${subtitleClassName}`}
          >
            YOUR AI COMPANION
          </span>
        </div>
      )}
    </div>
  );
};
