# Saarthi Design System Specification

## Visual Identity & Core Aesthetic
Saarthi is designed as a **futuristic, dark-mode local AI command center**. It communicates intelligence, privacy, control, local execution, and high reliability.

---

## 1. Color Palette

### Base Dark Surfaces
- **Obsidian Background**: `#0b0f19` (`bg-slate-950` / `bg-neutral-950`)
- **Panel Surface**: `#111827` (`bg-slate-900`)
- **Card Surface**: `#1f2937` (`bg-slate-800` / `bg-slate-800/80`)
- **Border Neutral**: `#374151` (`border-slate-700`)

### Brand Highlights & Accent Colors
- **Amber / Saffron Primary**: `#f59e0b` (`amber-500` / `amber-400`)
- **Emerald Success**: `#10b981` (`emerald-500` / `emerald-400`)
- **Sky Info**: `#38bdf8` (`sky-400`)
- **Rose / Red Warning**: `#f43f5e` (`rose-500`)

---

## 2. Typography & Hierarchy
- **Primary Font Family**: Inter, system-ui, sans-serif
- **Code Font Family**: JetBrains Mono, Fira Code, monospace
- **Headings**: `text-xl font-bold tracking-tight text-slate-100`
- **Body Text**: `text-sm font-normal text-slate-300 leading-relaxed`
- **Muted Text**: `text-xs font-normal text-slate-400`

---

## 3. Cards, Badges & Status Indicators
- **Local Badge**: `inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20`
- **Risk Badge (High)**: `inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20`
- **Status Indicator (Online)**: `h-2 w-2 rounded-full bg-emerald-500 animate-pulse`
- **Status Indicator (Offline)**: `h-2 w-2 rounded-full bg-rose-500`

---

## 4. UI Components Specification
- **Buttons**:
  - Primary: `bg-amber-500 hover:bg-amber-400 text-slate-950 font-medium px-4 py-2 rounded-lg transition-colors`
  - Secondary: `bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-4 py-2 rounded-lg transition-colors`
  - Danger/Deny: `bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 px-4 py-2 rounded-lg transition-colors`
- **Message Bubbles**:
  - User: `bg-amber-500/10 border border-amber-500/20 text-slate-200 rounded-2xl rounded-tr-none px-4 py-3`
  - Assistant: `bg-slate-900 border border-slate-800 text-slate-200 rounded-2xl rounded-tl-none px-4 py-3`
