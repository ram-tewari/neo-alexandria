/**
 * PDF.js Worker Configuration
 * 
 * This file configures the PDF.js worker for react-pdf.
 * The worker is required for PDF rendering and must be loaded before using react-pdf.
 */

import { pdfjs } from 'react-pdf';

// Configure PDF.js worker
// Using CDN for the worker to avoid bundling issues
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export { pdfjs };
