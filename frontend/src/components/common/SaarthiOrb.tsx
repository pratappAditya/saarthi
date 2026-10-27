import React from "react";
import { motion } from "motion/react";

export type SaarthiOrbState =
  | "idle"
  | "listening"
  | "thinking"
  | "searching"
  | "running_tool"
  | "waiting_permission"
  | "reading_memory"
  | "reading_files"
  | "responding"
  | "error";

interface SaarthiOrbProps {
  state?: SaarthiOrbState;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  onClick?: () => void;
}

export const SaarthiOrb: React.FC<SaarthiOrbProps> = ({
  state = "idle",
  size = "md",
  className = "",
  onClick,
}) => {
  const containerSizes = {
    sm: "w-16 h-16",
    md: "w-32 h-32",
    lg: "w-48 h-48",
    xl: "w-60 h-60",
  };

  // State configurations (color, animation speeds, opacity)
  const stateConfig: Record<
    SaarthiOrbState,
    {
      glowColor: string;
      coreColor: string;
      innerCoreColor: string;
      glowOpacity: number[];
      glowScale: number[];
      rotSpeedInner: number;
      rotSpeedOuter: number;
      label: string;
    }
  > = {
    idle: {
      glowColor: "bg-[#F59E0B]/20",
      coreColor: "bg-[#F59E0B]/40",
      innerCoreColor: "bg-[#F59E0B]",
      glowOpacity: [0.15, 0.25, 0.15],
      glowScale: [1, 1.05, 1],
      rotSpeedInner: 25,
      rotSpeedOuter: 35,
      label: "IDLE",
    },
    listening: {
      glowColor: "bg-[#EAB308]/25",
      coreColor: "bg-[#EAB308]/50",
      innerCoreColor: "bg-[#EAB308]",
      glowOpacity: [0.25, 0.45, 0.25],
      glowScale: [1, 1.15, 1],
      rotSpeedInner: 12,
      rotSpeedOuter: 18,
      label: "LISTENING",
    },
    thinking: {
      glowColor: "bg-[#F59E0B]/30",
      coreColor: "bg-[#F59E0B]/60",
      innerCoreColor: "bg-[#F59E0B]",
      glowOpacity: [0.3, 0.5, 0.3],
      glowScale: [1, 1.1, 1],
      rotSpeedInner: 5,
      rotSpeedOuter: 8,
      label: "THINKING",
    },
    searching: {
      glowColor: "bg-amber-500/25",
      coreColor: "bg-amber-400/50",
      innerCoreColor: "bg-amber-500",
      glowOpacity: [0.2, 0.4, 0.2],
      glowScale: [1, 1.2, 1],
      rotSpeedInner: 8,
      rotSpeedOuter: 12,
      label: "SEARCHING",
    },
    running_tool: {
      glowColor: "bg-amber-600/30",
      coreColor: "bg-amber-500/60",
      innerCoreColor: "bg-amber-400",
      glowOpacity: [0.35, 0.6, 0.35],
      glowScale: [1, 1.15, 1],
      rotSpeedInner: 3,
      rotSpeedOuter: 5,
      label: "RUNNING TOOL",
    },
    waiting_permission: {
      glowColor: "bg-rose-500/20",
      coreColor: "bg-[#F59E0B]/50",
      innerCoreColor: "bg-rose-500",
      glowOpacity: [0.4, 0.7, 0.4],
      glowScale: [0.95, 1.05, 0.95],
      rotSpeedInner: 40,
      rotSpeedOuter: 60,
      label: "WAITING PERMISSION",
    },
    reading_memory: {
      glowColor: "bg-[#F59E0B]/25",
      coreColor: "bg-[#EAB308]/60",
      innerCoreColor: "bg-[#F59E0B]",
      glowOpacity: [0.25, 0.45, 0.25],
      glowScale: [1, 1.1, 1],
      rotSpeedInner: 10,
      rotSpeedOuter: 15,
      label: "READING MEMORY",
    },
    reading_files: {
      glowColor: "bg-[#F59E0B]/20",
      coreColor: "bg-zinc-400/40",
      innerCoreColor: "bg-[#F59E0B]",
      glowOpacity: [0.2, 0.35, 0.2],
      glowScale: [1, 1.08, 1],
      rotSpeedInner: 15,
      rotSpeedOuter: 20,
      label: "READING FILES",
    },
    responding: {
      glowColor: "bg-[#F59E0B]/35",
      coreColor: "bg-[#F59E0B]/70",
      innerCoreColor: "bg-white",
      glowOpacity: [0.3, 0.65, 0.3],
      glowScale: [1, 1.25, 1],
      rotSpeedInner: 18,
      rotSpeedOuter: 24,
      label: "RESPONDING",
    },
    error: {
      glowColor: "bg-rose-500/30",
      coreColor: "bg-rose-500/50",
      innerCoreColor: "bg-rose-600",
      glowOpacity: [0.4, 0.8, 0.4],
      glowScale: [0.95, 1.1, 0.95],
      rotSpeedInner: 50,
      rotSpeedOuter: 70,
      label: "ERROR",
    },
  };

  const current = stateConfig[state] || stateConfig.idle;

  return (
    <div
      onClick={onClick}
      className={`relative flex items-center justify-center select-none group cursor-pointer ${className}`}
    >
      {/* Outer ambient glow */}
      <motion.div
        animate={{
          scale: current.glowScale,
          opacity: current.glowOpacity,
        }}
        transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        className={`absolute inset-0 ${current.glowColor} rounded-full blur-[40px] scale-110`}
      />

      {/* Main Container Orb */}
      <div
        className={`relative ${containerSizes[size]} rounded-full border border-white/10 bg-[#0D0D0D] flex items-center justify-center overflow-hidden shadow-2xl transition-all group-hover:border-[#F59E0B]/40`}
      >
        {/* Layered circles for geometric depth */}
        <motion.div
          animate={{
            rotate: [45, 405],
          }}
          transition={{
            duration: current.rotSpeedOuter,
            repeat: Infinity,
            ease: "linear",
          }}
          className="absolute w-[82%] h-[82%] border border-white/5 rounded-full"
        />

        <motion.div
          animate={{
            rotate: [-12, -372],
          }}
          transition={{
            duration: current.rotSpeedInner,
            repeat: Infinity,
            ease: "linear",
          }}
          className="absolute w-[68%] h-[68%] border border-white/10 rounded-full"
        />

        {/* Inner Glowing Core */}
        <motion.div
          animate={{
            scale: [1, 1.15, 1],
            opacity: [0.25, 0.45, 0.25],
          }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          className={`w-[40%] h-[40%] ${current.coreColor} rounded-full blur-[15px]`}
        />

        <motion.div
          animate={{
            scale: [1, 1.06, 1],
          }}
          transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
          className={`w-[15%] h-[15%] rounded-full ${current.innerCoreColor} shadow-[0_0_15px_rgba(245,158,11,0.5)]`}
        />

        {/* Orbital Particles */}
        <div className="absolute top-[22%] right-[26%] w-1.5 h-1.5 bg-[#F59E0B] rounded-full opacity-60 shadow-[0_0_6px_#F59E0B]" />
        <div className="absolute bottom-[30%] left-[22%] w-1 h-1 bg-white rounded-full opacity-40" />
      </div>

      {/* Floating State Badge */}
      <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 px-2.5 py-0.5 rounded-full bg-[#0D0D0D] border border-white/10 text-[9px] font-mono text-zinc-300 tracking-wider flex items-center gap-1.5 backdrop-blur-md shadow-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            state === "error"
              ? "bg-rose-500 animate-pulse"
              : state === "waiting_permission"
              ? "bg-rose-400"
              : "bg-[#F59E0B] animate-ping"
          }`}
        />
        <span>SAARTHI: {current.label}</span>
      </div>
    </div>
  );
};

