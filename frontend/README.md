# Sheetaro Frontend

Next.js web application for the Sheetaro print ordering system.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | No | `http://localhost:3001` |

## Testing

### Unit Tests (Vitest)

```bash
# Run all unit tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

### E2E Tests (Playwright)

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all E2E tests
npx playwright test

# Run E2E tests with UI
npx playwright test --ui

# Run specific test file
npx playwright test e2e/auth.spec.ts

# Show test report
npx playwright show-report
```

## Project Structure

```
frontend/
├── e2e/                        # E2E tests (Playwright)
│   ├── auth.spec.ts           # Authentication flow tests
│   ├── order.spec.ts          # Order creation tests
│   └── admin.spec.ts          # Admin panel tests
├── public/
│   └── fonts/                  # IranYekan font files
├── src/
│   ├── __tests__/             # Unit tests (Vitest)
│   │   ├── components/        # Component tests
│   │   ├── hooks/             # Hook tests
│   │   ├── pages/             # Page tests
│   │   ├── mocks/             # MSW mock handlers
│   │   ├── setup.ts           # Test setup
│   │   └── utils/             # Test utilities
│   ├── app/                   # Next.js App Router pages
│   │   ├── (auth)/            # Auth pages (login, register, verify)
│   │   ├── (dashboard)/       # Protected dashboard pages
│   │   └── layout.tsx         # Root layout
│   ├── components/
│   │   ├── layout/            # Layout components (Header, Sidebar, Footer)
│   │   └── ui/                # Reusable UI components
│   ├── hooks/                 # Custom React hooks
│   │   ├── useAuth.ts         # Authentication hook
│   │   ├── useCatalog.ts      # Catalog data hook
│   │   └── useOrders.ts       # Orders data hook
│   ├── lib/
│   │   ├── api.ts             # Axios API client
│   │   ├── auth.ts            # Auth utilities
│   │   └── utils.ts           # Helper functions
│   └── types/                 # TypeScript types
├── playwright.config.ts       # Playwright configuration
├── vitest.config.ts           # Vitest configuration
└── tailwind.config.ts         # Tailwind CSS configuration
```

## Features

### Authentication
- Phone + password registration
- JWT-based session management
- Telegram account linking via OTP

### Orders
- Multi-step order creation flow
- Category and plan selection
- Questionnaire for semi-private designs
- Template selection for public designs
- Order tracking and history

### Payments
- Card-to-card payment flow
- Receipt upload
- Payment status tracking

### Admin Panel
- Payment approval/rejection
- Catalog management
- User management

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Testing**: Vitest + Testing Library + MSW + Playwright
- **Icons**: Lucide React

## Test Coverage

### Unit Tests

| Category | Files | Description |
|----------|-------|-------------|
| Components | `Button.test.tsx`, `Input.test.tsx`, `Modal.test.tsx` | UI component tests |
| Hooks | `useAuth.test.tsx`, `useOrders.test.tsx` | Custom hook tests |
| Pages | `login.test.tsx`, `register.test.tsx`, `dashboard.test.tsx` | Page component tests |

### E2E Tests

| File | Description |
|------|-------------|
| `auth.spec.ts` | Registration, login, logout, session persistence |
| `order.spec.ts` | Order creation, payment upload, order list |
| `admin.spec.ts` | Payment approval, admin dashboard |

## Development

### Code Quality

```bash
# Run linting
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format
```

### Building

```bash
# Development build
npm run dev

# Production build
npm run build

# Analyze bundle
ANALYZE=true npm run build
```

## Docker

```bash
# Build image
docker build -t sheetaro-frontend .

# Run container
docker run -p 3000:3000 sheetaro-frontend
```

---

**Last Updated**: 2026-01-21
