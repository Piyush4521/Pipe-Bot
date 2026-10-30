import { useEffect } from 'react';
import { SYSTEM_INFO } from '@/constants/system';

export function useDocumentTitle(title?: string): void {
  useEffect(() => {
    if (title) {
      if (title.startsWith(SYSTEM_INFO.NAME)) {
        document.title = title;
      } else {
        document.title = `${SYSTEM_INFO.NAME} | ${title}`;
      }
    } else {
      document.title = `${SYSTEM_INFO.NAME} | Intelligent Pipeline Inspection`;
    }
  }, [title]);
}

