import type { FC } from 'react';
import { Outlet } from 'react-router-dom';
import { Navigation } from './Navigation';
import { PageContainer } from '@/components/ui/PageContainer';
import { SYSTEM_INFO } from '@/constants/system';

export const RootLayout: FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-industrial-50 text-industrial-900">
      <Navigation />

      <div className="flex-1">
        <PageContainer maxWidth="2xl">
          <Outlet />
        </PageContainer>
      </div>

      <footer className="bg-white border-t border-industrial-200 mt-auto py-4 text-xs text-industrial-500">
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-industrial-800">{SYSTEM_INFO.NAME}</span>
            <span>/</span>
            <span>{SYSTEM_INFO.CURRENT_STAGE}</span>
          </div>
          <div className="font-mono text-[11px] text-industrial-400">
            Hardware Stack: {SYSTEM_INFO.SPECIFICATION.CONTROLLER} | {SYSTEM_INFO.SPECIFICATION.CAMERA} | {SYSTEM_INFO.SPECIFICATION.INFERENCE_ENGINE}
          </div>
        </div>
      </footer>
    </div>
  );
};
