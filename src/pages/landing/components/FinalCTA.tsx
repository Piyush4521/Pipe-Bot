import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ArrowRight, Cpu, LayoutDashboard } from 'lucide-react';

export const FinalCTA: FC = () => {
  const scrollToArchitecture = () => {
    const el = document.getElementById('architecture');
    if (el) {
      const navOffset = 70;
      const elementPosition = el.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - navOffset;
      window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
    }
  };

  return (
    <section className="py-16 lg:py-24 bg-industrial-950 text-white border-b border-industrial-800">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          {/* Engineering Badge */}
          <div className="inline-flex items-center gap-2">
            <Badge variant="brand" isMono className="text-xs px-2.5 py-1">
              Operator Console Ready
            </Badge>
          </div>

          {/* Headline */}
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Explore the PipeBot Inspection Platform.
          </h2>

          {/* Supporting Text */}
          <p className="text-base sm:text-lg text-industrial-300 max-w-2xl mx-auto leading-relaxed">
            Review the operator dashboard, inspect simulated defect records, explore sensor odometry structures, and evaluate the planned hardware pipeline architecture.
          </p>

          {/* CTA Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <NavLink to={ROUTES.DASHBOARD.ROOT} className="w-full sm:w-auto">
              <Button
                variant="primary"
                size="lg"
                className="w-full sm:w-auto"
                leftIcon={<LayoutDashboard className="w-5 h-5" />}
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Open Dashboard
              </Button>
            </NavLink>

            <Button
              variant="outline"
              size="lg"
              onClick={scrollToArchitecture}
              className="w-full sm:w-auto bg-industrial-900 border-industrial-700 text-industrial-100 hover:bg-industrial-800"
              leftIcon={<Cpu className="w-4 h-4 text-brand-orange" />}
            >
              System Architecture
            </Button>
          </div>

          {/* Operational Disclaimer */}
          <div className="pt-8 border-t border-industrial-800 max-w-xl mx-auto text-xs text-industrial-400 font-mono">
            <p>
              Note: This is an engineering research prototype under active development. Live ESP32 hardware and video feeds are engaged during scheduled physical conduit test runs.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
