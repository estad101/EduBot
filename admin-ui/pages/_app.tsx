import 'tailwindcss/tailwind.css';
import type { AppProps } from 'next/app';
import { useEffect } from 'react';

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    // Update current time in the UI
    const updateTime = () => {
      const timeElement = document.getElementById('current-time');
      if (timeElement) {
        const now = new Date();
        timeElement.textContent = now.toLocaleTimeString();
      }
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return <Component {...pageProps} />;
}
