import React from "react";
import StatusIndicator from "./StatusIndicator";
import WhatsAppIndicator from "./WhatsAppIndicator";

// Updated layout with mobile-friendly sidebar menu
interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

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
    <div className="flex h-screen bg-gray-100 w-full">
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 lg:hidden z-30"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 w-64 bg-blue-900 text-white shadow-lg transition-transform duration-300 ease-in-out transform z-40 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0 h-screen overflow-y-auto flex flex-col`}
      >
        {/* Logo Section */}
        <div className="p-6 border-b border-blue-800 flex-shrink-0">
          <h1 className="text-2xl font-bold">WhatsApp Bot</h1>
          <p className="text-blue-200 text-sm">Admin Panel</p>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 py-6 overflow-y-auto">
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

      {/* Main Content */}
      <main className="flex-1 flex flex-col w-full min-w-0">
        {/* Top Bar */}
        <div className="bg-white shadow-sm z-20 flex-shrink-0">
          <div className="px-3 sm:px-6 lg:px-8 py-3 sm:py-4 flex justify-between items-center gap-2 sm:gap-4 min-h-16">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded transition flex-shrink-0"
              aria-label="Toggle sidebar"
            >
              <i className={`fas ${sidebarOpen ? "fa-times" : "fa-bars"} text-lg text-gray-700`}></i>
            </button>

            {/* Title */}
            <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-800 truncate flex-1">
              Admin
            </h2>

            {/* Right Section */}
            <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
              <div className="hidden md:flex items-center gap-2 sm:gap-4">
                <StatusIndicator />
                <WhatsAppIndicator />
              </div>

              {/* Notifications */}
              <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition flex-shrink-0">
                <i className="fas fa-bell text-lg"></i>
              </button>

              {/* Logout */}
              <div className="border-l border-gray-300 pl-2 sm:pl-4 flex-shrink-0">
                <a
                  href="/logout"
                  className="text-gray-600 hover:text-red-600 transition flex items-center gap-1"
                >
                  <i className="fas fa-sign-out-alt text-lg"></i>
                  <span className="hidden sm:inline text-sm font-medium">Logout</span>
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="flex-1 overflow-auto w-full">
          <div className="p-3 sm:p-6 lg:p-8 w-full h-full">{children}</div>
        </div>
      </main>
    </div>
  );
}
