import { create } from "zustand";

interface DashboardState {
  totalStudents: number;
  activeSubscribers: number;
  totalRevenue: number;
  systemHealth: string;
  setStats: (stats: Partial<DashboardState>) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  totalStudents: 0,
  activeSubscribers: 0,
  totalRevenue: 0,
  systemHealth: "operational",
  setStats: (stats) => set(stats),
}));
