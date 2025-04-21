import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import { useEffect, useState } from 'react';

export default function App({ Component, pageProps }: AppProps) {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Load theme from localStorage if exists
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    if (newTheme) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  return (
    <>
      {/* Floating theme toggle button */}
      <button
        onClick={toggleTheme}
        className="fixed top-4 right-4 z-50 bg-white dark:bg-gray-800 text-black dark:text-white px-3 py-1 rounded shadow hover:opacity-90 transition"
      >
        {isDarkMode ? '🌙 Dark' : '☀️ Light'}
      </button>

      <Component {...pageProps} />
    </>
  );
}
