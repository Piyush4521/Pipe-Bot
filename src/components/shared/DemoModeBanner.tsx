import type { FC } from 'react';
import { useAppMode } from '@/app/providers/AppContext';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Sparkles, PowerOff } from 'lucide-react';

export const DemoModeBanner: FC = () => {
  const { isDemoMode, toggleDemoMode } = useAppMode();

  if (!isDemoMode) return null;

  return (
    <div className="bg-brand-orange text-white px-4 py-2 border-b border-brand-orange-hover text-xs font-mono flex flex-col sm:flex-row items-center justify-between gap-2 shadow-industrial-sm select-none">
      <div className="flex items-center gap-2.5">
        <div className="p-1 bg-white/20 rounded-sm">
          <Sparkles className="w-3.5 h-3.5 text-white" />
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" isMono className="bg-white text-brand-orange border-white font-bold text-[10px]">
            DEMO MODE ACTIVE
          </Badge>
          <span className="text-[11px] font-medium text-white/90">
            Displaying simulated test data for frontend interface validation. No live hardware commands will be sent.
          </span>
        </div>
      </div>

      <Button
        variant="secondary"
        size="sm"
        onClick={toggleDemoMode}
        className="h-6 text-[10px] bg-industrial-950 border-industrial-950 text-white hover:bg-industrial-900"
        leftIcon={<PowerOff className="w-3 h-3" />}
      >
        Exit Demo Mode
      </Button>
    </div>
  );
};

