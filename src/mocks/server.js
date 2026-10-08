import { setupServer } from 'msw/node';
import { handlers } from './subscriptionHandlers';

export const server = setupServer(...handlers);