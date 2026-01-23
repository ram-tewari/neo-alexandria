/**
 * MSW Server Setup
 * 
 * Sets up Mock Service Worker for testing
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Create MSW server with handlers
export const server = setupServer(...handlers);
