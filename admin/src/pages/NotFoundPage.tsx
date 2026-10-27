import React from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { HelpCircle, ArrowLeft } from 'lucide-react';

interface NotFoundPageProps {
  onNavigateHome: () => void;
}

export const NotFoundPage: React.FC<NotFoundPageProps> = ({ onNavigateHome }) => {
  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4">
      <Card className="max-w-md w-full p-8 text-center border-slate-800 bg-slate-900/90 shadow-2xl">
        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-800/60 border border-slate-700 flex items-center justify-center text-indigo-400">
          <HelpCircle className="w-8 h-8" />
        </div>
        <h1 className="text-xl font-bold text-slate-100">Page Not Found (404)</h1>
        <p className="text-sm text-slate-400 mt-2 mb-6">
          The requested administrative module or view could not be located on this control plane instance.
        </p>
        <Button onClick={onNavigateHome} className="w-full">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Return to Overview
        </Button>
      </Card>
    </div>
  );
};
