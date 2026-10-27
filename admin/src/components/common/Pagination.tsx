import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './Button';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems?: number;
  pageSize?: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  pageSize,
  onPageChange,
  className = ''
}) => {
  if (totalPages <= 1 && !totalItems) return null;

  return (
    <div className={`flex items-center justify-between gap-4 text-xs text-slate-400 ${className}`}>
      <div>
        {totalItems !== undefined && pageSize !== undefined ? (
          <span>
            Showing{' '}
            <span className="font-mono text-slate-200">
              {Math.min((currentPage - 1) * pageSize + 1, totalItems)}
            </span>{' '}
            to{' '}
            <span className="font-mono text-slate-200">
              {Math.min(currentPage * pageSize, totalItems)}
            </span>{' '}
            of <span className="font-mono text-slate-200">{totalItems}</span> results
          </span>
        ) : (
          <span>
            Page <span className="font-mono text-slate-200">{currentPage}</span> of{' '}
            <span className="font-mono text-slate-200">{Math.max(1, totalPages)}</span>
          </span>
        )}
      </div>
      <div className="flex items-center gap-1.5">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
        >
          <ChevronLeft className="w-3.5 h-3.5" />
          <span>Prev</span>
        </Button>
        <span className="px-2 font-mono text-[11px] text-slate-300">
          {currentPage} / {Math.max(1, totalPages)}
        </span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
        >
          <span>Next</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </Button>
      </div>
    </div>
  );
};
