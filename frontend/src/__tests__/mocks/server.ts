/**
 * MSW server setup for Node.js testing environment
 */

import { setupServer } from "msw/node";
import { handlers } from "./handlers";

// Create the server instance with default handlers
export const server = setupServer(...handlers);

