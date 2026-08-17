/**
 * usePageMeta.js
 * Sets document.title and meta description for each page.
 * Works inside a React SPA without react-helmet.
 */
import { useEffect } from 'react';

const SITE_NAME = 'URL-Tracer — Cyber Attack Detection & IP Intelligence';

export default function usePageMeta(title, description) {
  useEffect(() => {
    // Set browser tab title
    document.title = title ? `${title} | ${SITE_NAME}` : SITE_NAME;

    // Update or create meta description
    let meta = document.querySelector('meta[name="description"]');
    if (!meta) {
      meta = document.createElement('meta');
      meta.setAttribute('name', 'description');
      document.head.appendChild(meta);
    }
    if (description) meta.setAttribute('content', description);

    // Update OG title
    let ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle && title) ogTitle.setAttribute('content', `${title} | ${SITE_NAME}`);

    // Update OG description
    let ogDesc = document.querySelector('meta[property="og:description"]');
    if (ogDesc && description) ogDesc.setAttribute('content', description);

    // Restore on unmount
    return () => {
      document.title = SITE_NAME;
    };
  }, [title, description]);
}
