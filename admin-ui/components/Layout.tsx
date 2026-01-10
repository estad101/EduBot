import React, { useState, useEffect } from "react";
import StatusIndicator from "./StatusIndicator";
import WhatsAppIndicator from "./WhatsAppIndicator";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [appName, setAppName] = useState('WhatsApp Bot');

  // Fetch app name from admin_settings table on component mount
  useEffect(() => {
    const fetchAppName = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const settingsUrl = `${apiUrl}/api/admin/settings`;
        
        const response = await fetch(settingsUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data?.data?.bot_name && data.data.bot_name.trim()) {
            setAppName(data.data.bot_name);
          }
        }
      } catch (err) {
        console.error('Error fetching app name:', err);
      }
    };

    fetchAppName();
  }, []);

  const menuItems = [
    { href: "/dashboard", icon: "fa-chart-line", label: "Dashboard" },
    { href: "/conversations", icon: "fa-whatsapp", label: "Conversations" },
    { href: "/leads", icon: "fa-list", label: "Leads" },
    { href: "/students", icon: "fa-users", label: "Students" },
    { href: "/payments", icon: "fa-credit-card", label: "Payments" },
    { href: "/subscriptions", icon: "fa-calendar-alt", label: "Subscriptions" },
    { href: "/homework", icon: "fa-book", label: "Homework" },
    { href: "/reports", icon: "fa-chart-bar", label: "Reports" },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 lg:hidden z-30"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Main Layout Container */}
      <div className="flex w-full h-full bg-gray-100">
        {/* Sidebar */}
        <aside
          className={`fixed top-0 left-0 w-64 h-full bg-blue-900 text-white shadow-lg transition-all duration-300 ease-in-out z-40 lg:relative lg:translate-x-0 overflow-y-auto ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          {/* Logo Section */}
          <div className="p-6 border-b border-blue-800 flex-shrink-0">
            <h1 className="text-2xl font-bold">{appName}</h1>
            <p className="text-blue-200 text-sm">Admin Panel</p>
          </div>

          {/* Navigation Menu */}
          <nav className="py-6">
            <div className="space-y-2">
              {menuItems.map((item) => (
                <a
                  key={item.href}
                  href={item.href}
                  className="flex items-center px-6 py-3 text-blue-100 hover:bg-blue-800 hover:text-white transition duration-200"
                  onClick={() => setSidebarOpen(false)}
                >
                  <i className={`fas ${item.icon} mr-3 w-5`}></i>
                  <span className="text-sm sm:text-base">{item.label}</span>
                </a>
              ))}
            </div>

            {/* Settings Section */}
            <div className="mt-8 pt-6 border-t border-blue-800">
              <a
                href="/settings"
                className="flex items-center px-6 py-3 text-blue-100 hover:bg-blue-800 hover:text-white transition duration-200"
                onClick={() => setSidebarOpen(false)}
              >
                <i className="fas fa-cog mr-3 w-5"></i>
                <span className="text-sm sm:text-base">Settings</span>
              </a>
            </div>
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Top Bar */}
          <div className="bg-white shadow-sm z-20 flex-shrink-0 border-b border-gray-200 h-16 flex items-center px-4 sm:px-6 lg:px-8 gap-4">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded transition flex-shrink-0 -ml-2"
              aria-label="Toggle sidebar"
            >
              <i className={`fas ${sidebarOpen ? "fa-times" : "fa-bars"} text-lg text-gray-700`}></i>
            </button>

            {/* Title */}
            <h2 className="text-lg sm:text-xl font-bold text-gray-800 flex-1 min-w-0">
              Admin
            </h2>

            {/* Status Indicators - Desktop Only */}
            <div className="hidden md:flex items-center gap-3 flex-shrink-0">
              <StatusIndicator />
              <WhatsAppIndicator />
            </div>

            {/* Notifications */}
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition flex-shrink-0">
              <i className="fas fa-bell text-lg"></i>
            </button>

            {/* Logout */}
            <div className="border-l border-gray-300 pl-3 sm:pl-4 flex-shrink-0">
              <a
                href="/logout"
                className="text-gray-600 hover:text-red-600 transition flex items-center gap-1"
              >
                <i className="fas fa-sign-out-alt text-lg"></i>
                <span className="hidden sm:inline text-sm font-medium">Logout</span>
              </a>
            </div>
          </div>

          {/* Page Content */}
          <div className="flex-1 overflow-auto">
            <div className="p-4 sm:p-6 lg:p-8">{children}</div>
          </div>
        </main>
      </div>
    </>
  );
}
