import React from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

interface UnauthorizedPageProps {
  onNavigateHome: () => void;
}

export const UnauthorizedPage: React.FC<UnauthorizedPageProps> = ({ onNavigateHome }) => {
  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4">
      <Card className="max-w-md w-full p-8 text-center border-rose-900/40 bg-slate-900/90 shadow-2xl">
        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-rose-950/60 border border-rose-800 flex items-center justify-center text-rose-400">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h1 className="text-xl font-bold text-slate-100">Access Denied (403)</h1>
        <p className="text-sm text-slate-400 mt-2 mb-6">
          Your current administrative role does not have authorization to view this resource. Contact a SUPER_ADMIN to adjust your permission tier.
        </p>
        <Button onClick={onNavigateHome} className="w-full">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Return to Overview
        </Button>
      </Card>
    </div>
  );
};
