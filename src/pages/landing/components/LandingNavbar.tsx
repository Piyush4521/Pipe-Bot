import { useState, type FC } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { SYSTEM_INFO } from '@/constants/system';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  Menu,
  X,
  ArrowRight,
  LayoutDashboard,
  Cpu,
  Layers,
  GitBranch,
  ShieldAlert,
  Sliders,
} from 'lucide-react';

export const LandingNavbar: FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const scrollToSection = (id: string) => {
    setMobileMenuOpen(false);

    if (location.pathname !== ROUTES.HOME) {
      navigate(`/#${id}`);
      return;
    }

    const element = document.getElementById(id);
    if (element) {
      const navOffset = 70;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - navOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth',
      });
    }
  };

  const navLinks = [
    { label: 'Overview', id: 'overview', icon: Layers },
    { label: 'Process', id: 'process', icon: GitBranch },
    { label: 'Architecture', id: 'architecture', icon: Cpu },
    { label: 'Capabilities', id: 'capabilities', icon: ShieldAlert },
    { label: 'Technology', id: 'technology', icon: Sliders },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-industrial-200">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Identity */}
          <NavLink
            to={ROUTES.HOME}
            onClick={() => {
              if (location.pathname === ROUTES.HOME) {
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }
            }}
            className="flex items-center gap-3 group focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-orange"
            aria-label="PipeBot Home"
          >
            <div className="w-9 h-9 bg-industrial-900 flex items-center justify-center rounded-sm text-brand-orange border border-industrial-900 group-hover:border-brand-orange transition-colors shrink-0">
              <svg className="w-5 h-5" viewBox="0 0 32 32" fill="none" aria-hidden="true">
                <circle cx="16" cy="16" r="10" stroke="#CBD5E1" strokeWidth="2.5" />
                <circle cx="16" cy="16" r="5" stroke="#EA580C" strokeWidth="2" />
                <line x1="16" y1="2" x2="16" y2="7" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
                <line x1="16" y1="25" x2="16" y2="30" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
                <line x1="2" y1="16" x2="7" y2="16" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
                <line x1="25" y1="16" x2="30" y2="16" stroke="#EA580C" strokeWidth="2" strokeLinecap="square" />
              </svg>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="text-base font-bold tracking-wider uppercase text-industrial-900 leading-none">
                  {SYSTEM_INFO.NAME}
                </span>
                <Badge variant="brand" isMono className="text-[10px] py-0 px-1.5">
                  Research Prototype
                </Badge>
              </div>
              <span className="text-[10px] uppercase font-mono text-industrial-500 tracking-wider mt-0.5">
                PVC Robotic Pipeline Inspection
              </span>
            </div>
          </NavLink>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1 text-sm font-medium text-industrial-700" aria-label="Main Navigation">
            {navLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => scrollToSection(link.id)}
                className="px-3 py-1.5 rounded-sm hover:text-industrial-900 hover:bg-industrial-100 transition-colors focus:outline-none focus-visible:ring-1 focus-visible:ring-brand-orange"
              >
                {link.label}
              </button>
            ))}

            <div className="h-4 w-px bg-industrial-200 mx-1" />

            <NavLink
              to={ROUTES.DASHBOARD.ROOT}
              className="px-3 py-1.5 rounded-sm text-industrial-700 hover:text-brand-orange hover:bg-brand-orange-light transition-colors flex items-center gap-1.5 focus:outline-none focus-visible:ring-1 focus-visible:ring-brand-orange"
            >
              <LayoutDashboard className="w-4 h-4 text-industrial-500" />
              <span>Dashboard</span>
            </NavLink>
          </nav>

          {/* Desktop Right Action */}
          <div className="hidden sm:flex items-center gap-3">
            <NavLink to={ROUTES.DASHBOARD.ROOT}>
              <Button
                variant="primary"
                size="sm"
                rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
              >
                Launch Dashboard
              </Button>
            </NavLink>
          </div>

          {/* Mobile Menu Toggle Button */}
          <div className="flex items-center gap-2 lg:hidden">
            <NavLink to={ROUTES.DASHBOARD.ROOT} className="sm:hidden">
              <Button variant="primary" size="sm">
                Dashboard
              </Button>
            </NavLink>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 border border-industrial-300 rounded-sm text-industrial-700 hover:bg-industrial-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-orange"
              aria-label={mobileMenuOpen ? 'Close Navigation Menu' : 'Open Navigation Menu'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-industrial-200 bg-white px-4 pt-3 pb-6 space-y-3 shadow-lg">
          <div className="flex flex-col space-y-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <button
                  key={link.id}
                  onClick={() => scrollToSection(link.id)}
                  className="flex items-center gap-2.5 px-3 py-2.5 text-sm font-medium text-industrial-800 hover:bg-industrial-100 rounded-sm text-left transition-colors"
                >
                  <Icon className="w-4 h-4 text-industrial-500" />
                  <span>{link.label}</span>
                </button>
              );
            })}
            <NavLink
              to={ROUTES.DASHBOARD.ROOT}
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-2.5 px-3 py-2.5 text-sm font-semibold text-brand-orange hover:bg-brand-orange-light rounded-sm transition-colors"
            >
              <LayoutDashboard className="w-4 h-4 text-brand-orange" />
              <span>Inspection Dashboard</span>
            </NavLink>
          </div>

          <div className="pt-2 border-t border-industrial-200">
            <NavLink
              to={ROUTES.DASHBOARD.ROOT}
              onClick={() => setMobileMenuOpen(false)}
              className="block w-full"
            >
              <Button
                variant="primary"
                size="md"
                className="w-full justify-center"
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Launch Inspection Platform
              </Button>
            </NavLink>
          </div>
        </div>
      )}
    </header>
  );
};

