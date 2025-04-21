# Financial Analysis Frontend

React/Next.js frontend for the Financial Analysis Agent.

## Features

- Real-time chat interface for interacting with the financial analysis agent
- Asset comparison tool for stocks and cryptocurrencies
- Responsive design with Tailwind CSS
- API integration with Python backend

## Running the Frontend

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) with your browser.

## Project Structure

```
frontend/
├── public/           # Static assets
├── src/
│   ├── app/          # Next.js App Router 
│   │   ├── api/      # API routes
│   │   └── page.tsx  # Main chat interface
│   ├── components/   # Reusable UI components
│   └── types.ts      # TypeScript type definitions
├── tailwind.config.js # Tailwind CSS configuration
└── package.json      # Project dependencies
```

## API Integration

The frontend communicates with the Python backend running on `http://localhost:5000/api/chat`. Make sure the backend is running before using the chat interface.

## Development Notes

- The frontend is built with Next.js and React
- Tailwind CSS is used for styling
- TypeScript is used for type safety

## Technologies Used

- Next.js
- React
- TypeScript
- Tailwind CSS

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
