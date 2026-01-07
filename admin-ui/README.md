# WhatsApp Bot Admin - React + Next.js

This is the Next.js React admin dashboard for the WhatsApp Chatbot API.

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Create `.env.local` file with API URL:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Default Login Credentials
Check your FastAPI `.env` file for `ADMIN_PASSWORD` to login

## Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
pages/           # Next.js pages (routes)
├── login.tsx    # Login page
├── dashboard.tsx # Main dashboard
├── students.tsx # Student management
├── payments.tsx # Payment tracking
├── subscriptions.tsx # Subscription management
├── homework.tsx # Homework submissions
├── reports.tsx  # Analytics & reports
└── settings.tsx # API configuration

components/
├── Layout.tsx   # Main layout with sidebar

lib/
├── api-client.ts # API client with axios

store/
├── auth.ts      # Authentication state (Zustand)
└── dashboard.ts # Dashboard state (Zustand)
```

## Features

✅ **Dashboard** - Real-time statistics and KPIs
✅ **Student Management** - View, search, filter students
✅ **Payment Tracking** - Monitor all transactions
✅ **Subscription Management** - Track active subscriptions
✅ **Homework Submissions** - View student submissions
✅ **Reports & Analytics** - Comprehensive analytics
✅ **Settings** - API configuration management
✅ **Authentication** - Secure login with session management
✅ **Responsive Design** - Works on desktop and mobile
✅ **Real-time Updates** - Auto-refresh dashboard every 30s

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checker

## API Integration

The app connects to FastAPI backend at `http://localhost:8000` by default. All API endpoints are in `lib/api-client.ts`:

```typescript
// Example
const response = await apiClient.getStudents(0, 50);
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### CORS Errors
Make sure FastAPI CORS is configured to accept requests from:
- `http://localhost:3000` (development)
- Your production domain

### Login Not Working
1. Verify `ADMIN_PASSWORD` is set in FastAPI `.env`
2. Check network tab in DevTools for API errors
3. Ensure FastAPI server is running

### API Calls Failing
1. Check if FastAPI is running on `:8000`
2. Verify `NEXT_PUBLIC_API_URL` in `.env.local`
3. Check browser console for specific error messages

## Support

For issues with the API integration, check the FastAPI README or logs.
