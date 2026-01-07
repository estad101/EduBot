import React from "react";
import StatusIndicator from "./StatusIndicator";
import WhatsAppIndicator from "./WhatsAppIndicator";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-0"
        } bg-blue-900 text-white shadow-lg transition-all duration-300 overflow-hidden`}
      >
        <div className="p-6">
          <h1 className="text-2xl font-bold">WhatsApp Bot</h1>
          <p className="text-blue-200 text-sm">Admin Panel</p>
        </div>

        <nav className="mt-8">
          <a
            href="/dashboard"
            className="flex items-center px-6 py-3 hover:bg-blue-800 transition"
          >
            <i className="fas fa-chart-line mr-3 w-5"></i>
            <span>Dashboard</span>
          </a>
          <a
            href="/students"
            className="flex items-center px-6 py-3 hover:bg-blue-800 transition"
          >
            <i className="fas fa-users mr-3 w-5"></i>
            <span>Students</span>
          </a>
          <a
            href="/payments"
            className="flex items-center px-6 py-3 hover:bg-blue-800 transition"
          >
            <i className="fas fa-credit-card mr-3 w-5"></i>
            <span>Payments</span>
          </a>
          <a
            href="/subscriptions"
            className="flex items-center px-6 py-3 hover:bg-blue-800 transition"
          >
            <i className="fas fa-calendar-alt mr-3 w-5"></i>
            <span>Subscriptions</span>
          </a>
          <a
            href="/homework"
            className="flex items-center px-6 py-3 hover:bg-blue-800 transition"
          >
            <i className="fas fa-book mr-3 w-5"></i>
            <span>Homework</span>
          </a>
          <a
            href="/reports"
            className="flex items-center px-6 py-3 hover:bg-blue-800 transition"
          >
            <i className="fas fa-chart-bar mr-3 w-5"></i>
            <span>Reports</span>
          </a>
          <a
            href="/settings"
            className="flex items-center px-6 py-3 hover:bg-blue-800 transition"
          >
            <i className="fas fa-cog mr-3 w-5"></i>
            <span>Settings</span>
          </a>
        </nav>

        <div className="absolute bottom-0 w-64 border-t border-blue-800 p-6">
          <a href="/logout" className="flex items-center text-blue-200 hover:text-white">
            <i className="fas fa-sign-out-alt mr-3 w-5"></i>
            <span>Logout</span>
          </a>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Top Bar */}
        <div className="bg-white shadow">
          <div className="px-8 py-4 flex justify-between items-center">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="md:hidden p-2 hover:bg-gray-100 rounded"
            >
              <i className="fas fa-bars text-lg"></i>
            </button>
            <h2 className="text-2xl font-bold text-gray-800">Admin Dashboard</h2>
            <div className="flex items-center space-x-6">
              <StatusIndicator />
              <WhatsAppIndicator />
              <span className="text-sm text-gray-600">
                <i className="far fa-clock mr-2"></i>
                <span id="current-time"></span>
              </span>
              <button className="text-gray-600 hover:text-gray-900">
                <i className="fas fa-bell text-lg"></i>
              </button>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
