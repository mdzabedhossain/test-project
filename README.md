# TEST-PROJECT

A Node.js web application built with **TypeScript** and **Next.js**.

## Tech Stack

| Layer           | Technology              |
| ---------------- | ----------------------- |
| Runtime          | Node.js                 |
| Language         | TypeScript              |
| Framework        | Next.js (App Router)    |
| Package Manager  | npm                     |

## Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later recommended)
- npm (comes with Node.js)

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd TEST-PROJECT
```

### 2. Install dependencies

```bash
npm install
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your local configuration. This project uses [dotenv](https://www.npmjs.com/package/dotenv) for environment variable management.

### 4. Run the development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

| Script   | Description                          |
| -------- | ------------------------------------ |
| `npm run dev`   | Start the Next.js development server |
| `npm run build` | Build the application for production |
| `npm run start` | Start the production server          |
| `npm run lint`  | Run ESLint                           |

> **Note:** Next.js scripts will be available once the framework is initialized.

## Project Structure

```
TEST-PROJECT/
├── app/              # Next.js App Router pages & layouts
├── components/       # Reusable React components
├── lib/              # Utility functions & shared logic
├── public/           # Static assets
├── types/            # TypeScript type definitions
├── cursor.md         # Cursor AI project guide
├── next.config.ts
├── package.json
└── tsconfig.json
```

## Development Guidelines

- Use TypeScript strict mode; avoid the `any` type
- Follow Next.js App Router conventions (`app/` directory)
- Prefer Server Components by default; use Client Components (`"use client"`) only when interactivity is required
- Keep changes focused and match existing project conventions

## License

ISC
