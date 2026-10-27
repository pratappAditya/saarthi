import React, { useState } from "react";
import { Check, ShieldCheck, Zap, Award, CreditCard, Key } from "lucide-react";
import { api } from "../../api";

interface PricingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onActivated?: () => void;
}

export function PricingModal({ isOpen, onClose, onActivated }: PricingModalProps) {
  const [licenseKeyInput, setLicenseKeyInput] = useState<string>("");
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  React.useEffect(() => {
    if (isOpen) {
      api.logTelemetryEvent("PRICING_VIEWED");
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleActivateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg(null);
    try {
      const res = await api.activateLicense(licenseKeyInput.trim());
      if (res.status === "ACTIVE") {
        setMsg("License successfully activated!");
        if (onActivated) onActivated();
        setTimeout(() => onClose(), 1500);
      } else {
        setMsg(`Activation status: ${res.status}. ${res.message || ""}`);
      }
    } catch (err: any) {
      setMsg(`Activation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden shadow-2xl">
        
        {/* HEADER */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
              <Zap className="w-4 h-4 text-cyan-400" />
              <span>Saarthi Commercial Plans & Licensing</span>
            </h2>
            <p className="text-[11px] text-slate-400">Vendor-authoritative entitlements. Local-first privacy guaranteed.</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 text-xs px-2 py-1 rounded">
            ✕ Close
          </button>
        </div>

        {/* BILLING TOGGLE */}
        <div className="flex items-center justify-center space-x-3 p-4 bg-slate-900/60 border-b border-slate-800">
          <span className={`text-xs ${billingCycle === "monthly" ? "text-cyan-300 font-bold" : "text-slate-400"}`}>Monthly</span>
          <button
            onClick={() => setBillingCycle(billingCycle === "monthly" ? "yearly" : "monthly")}
            className="w-10 h-5 bg-slate-800 rounded-full p-0.5 border border-slate-700 relative transition-all"
          >
            <div className={`w-4 h-4 bg-cyan-400 rounded-full transition-transform ${billingCycle === "yearly" ? "translate-x-5" : ""}`} />
          </button>
          <span className={`text-xs ${billingCycle === "yearly" ? "text-cyan-300 font-bold" : "text-slate-400"}`}>
            Yearly <span className="text-emerald-400 text-[10px] ml-1 font-semibold">(Save ~20%)</span>
          </span>
        </div>

        {/* PLAN CARDS GRID */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            
            {/* FREE PLAN */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-4">
              <div>
                <div className="text-xs font-bold text-slate-300">FREE</div>
                <div className="text-2xl font-extrabold text-slate-100 mt-1">₹0</div>
                <div className="text-[10px] text-slate-500">Free forever baseline</div>
                <ul className="mt-4 space-y-2 text-[11px] text-slate-400">
                  <li className="flex items-center"><Check className="w-3 h-3 text-cyan-400 mr-1.5" /> Local AI Chat & Memory</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-cyan-400 mr-1.5" /> Basic File Capabilities</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-amber-400 mr-1.5" /> Max 3 Job Apps / mo</li>
                  <li className="flex items-center text-slate-500">• Watermarked Exports</li>
                  <li className="flex items-center text-slate-600">✕ No Privileged Terminal</li>
                </ul>
              </div>
              <button disabled className="w-full bg-slate-800 text-slate-400 py-1.5 rounded text-xs">Current Plan</button>
            </div>

            {/* STUDENT PLAN */}
            <div className="bg-slate-950 p-4 rounded-xl border-2 border-cyan-500/60 relative flex flex-col justify-between space-y-4 shadow-lg shadow-cyan-500/10">
              <div className="absolute -top-3 right-3 bg-cyan-500 text-slate-950 text-[10px] font-extrabold px-2 py-0.5 rounded-full">
                BEST WEDGE
              </div>
              <div>
                <div className="text-xs font-bold text-cyan-300">STUDENT</div>
                <div className="text-2xl font-extrabold text-cyan-400 mt-1">
                  {billingCycle === "monthly" ? "₹149" : "₹1,299"}
                  <span className="text-xs font-normal text-slate-400">/{billingCycle === "monthly" ? "mo" : "yr"}</span>
                </div>
                <div className="text-[10px] text-slate-400">Requires .ac.in / .edu email</div>
                <ul className="mt-4 space-y-2 text-[11px] text-slate-300">
                  <li className="flex items-center font-semibold text-cyan-300"><Check className="w-3 h-3 text-cyan-400 mr-1.5" /> Watermark-Free Exports</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-cyan-400 mr-1.5" /> Unlimited Job Apps</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-cyan-400 mr-1.5" /> ATS Match & Tailoring</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-cyan-400 mr-1.5" /> Interview Prep Studio</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-cyan-400 mr-1.5" /> Email & Calendar Outreach</li>
                </ul>
              </div>
              <div className="text-[10px] text-slate-400 text-center">Supports UPI / Razorpay</div>
            </div>

            {/* PERSONAL PLAN */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-4">
              <div>
                <div className="text-xs font-bold text-purple-300">PERSONAL</div>
                <div className="text-2xl font-extrabold text-purple-400 mt-1">
                  {billingCycle === "monthly" ? "₹399" : "₹3,499"}
                  <span className="text-xs font-normal text-slate-400">/{billingCycle === "monthly" ? "mo" : "yr"}</span>
                </div>
                <div className="text-[10px] text-slate-500">For power job seekers</div>
                <ul className="mt-4 space-y-2 text-[11px] text-slate-300">
                  <li className="flex items-center font-semibold text-purple-300"><Check className="w-3 h-3 text-purple-400 mr-1.5" /> Watermark-Free Exports</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-purple-400 mr-1.5" /> All Student Features</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-purple-400 mr-1.5" /> Privileged Terminal Access</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-purple-400 mr-1.5" /> Extended Context Memory</li>
                </ul>
              </div>
              <div className="text-[10px] text-slate-400 text-center">Supports UPI / Cards</div>
            </div>

            {/* POWER PLAN */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-4">
              <div>
                <div className="text-xs font-bold text-amber-300">POWER</div>
                <div className="text-2xl font-extrabold text-amber-400 mt-1">
                  {billingCycle === "monthly" ? "₹999" : "₹8,999"}
                  <span className="text-xs font-normal text-slate-400">/{billingCycle === "monthly" ? "mo" : "yr"}</span>
                </div>
                <div className="text-[10px] text-slate-500">For engineers & power users</div>
                <ul className="mt-4 space-y-2 text-[11px] text-slate-300">
                  <li className="flex items-center font-semibold text-amber-300"><Check className="w-3 h-3 text-amber-400 mr-1.5" /> Watermark-Free Exports</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-amber-400 mr-1.5" /> Multi-device Binding (2)</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-amber-400 mr-1.5" /> Priority Ollama Engine</li>
                  <li className="flex items-center"><Check className="w-3 h-3 text-amber-400 mr-1.5" /> Max History Context (32)</li>
                </ul>
              </div>
              <div className="text-[10px] text-slate-400 text-center">Supports UPI / Cards</div>
            </div>

          </div>

          {/* LICENSE ACTIVATION FORM */}
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
            <h3 className="text-xs font-bold text-slate-200 flex items-center space-x-1.5">
              <Key className="w-4 h-4 text-cyan-400" />
              <span>Activate Purchased License Key</span>
            </h3>

            <form onSubmit={handleActivateKey} className="flex items-center space-x-2">
              <input
                type="text"
                required
                placeholder="SAARTHI-STU-XXXXXX..."
                value={licenseKeyInput}
                onChange={(e) => setLicenseKeyInput(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              />
              <button
                type="submit"
                disabled={loading}
                className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-medium px-4 py-1.5 rounded-lg text-xs transition-all shadow-md shadow-cyan-500/10"
              >
                {loading ? "Activating..." : "Activate Key"}
              </button>
            </form>

            {msg && <div className="text-xs text-cyan-300 bg-cyan-950/60 p-2 rounded border border-cyan-800">{msg}</div>}
          </div>

        </div>

      </div>
    </div>
  );
}
