import 'tailwindcss/tailwind.css';
import type { AppProps } from 'next/app';
import { useEffect } from 'react';
import Head from 'next/head';

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

  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
      </Head>
      <style jsx global>{`
        html,
        body {
          margin: 0;
          padding: 0;
          width: 100%;
          height: 100%;
          overflow: hidden;
          -webkit-touch-callout: none;
          -webkit-user-select: none;
        }
        #__next {
          width: 100%;
          height: 100%;
          display: flex;
        }
      `}</style>
      <Component {...pageProps} />
    </>
  );
}
