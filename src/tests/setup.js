import { vi } from 'vitest';
import '@testing-library/jest-dom';

// Mock fetch globally
global.fetch = vi.fn();

// Mock sessionStorage
global.sessionStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  clear: vi.fn(),
  removeItem: vi.fn(),
  key: vi.fn(),
  length: 0
};

// Mock localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  clear: vi.fn(),
  removeItem: vi.fn(),
  key: vi.fn(),
  length: 0
};

// Mock navigation
const navigate = vi.fn();
vi.mock('svelte-navigator', () => ({
  useNavigate: () => navigate,
  useLocation: vi.fn(() => ({ pathname: '/receipt-upload' })),
  Link: vi.fn()
}));

// Reset all mocks before each test
beforeEach(() => {
  vi.clearAllMocks();
}); 