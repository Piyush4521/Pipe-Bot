import type { ComponentType } from 'react';

export interface NavItem {
  id: string;
  label: string;
  path: string;
  icon?: ComponentType<{ className?: string }>;
  description?: string;
  badge?: string;
}

export interface NavigationSection {
  title?: string;
  items: NavItem[];
}

