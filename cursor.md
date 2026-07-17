# TEST-PROJECT

Cursor AI-এর জন্য প্রজেক্ট গাইড।

## Overview

এটি একটি **Node.js** প্রজেক্ট, যেখানে **TypeScript** এবং **Next.js** ব্যবহার করা হবে।

## Tech Stack

| Layer | Technology |
|-------|------------|
| Runtime | Node.js |
| Language | TypeScript |
| Framework | Next.js (App Router) |
| Package Manager | npm |

## Project Structure

```
TEST-PROJECT/
├── app/              # Next.js App Router pages & layouts
├── components/       # Reusable React components
├── lib/              # Utility functions & shared logic
├── public/           # Static assets
├── types/            # TypeScript type definitions
├── cursor.md
├── next.config.ts
├── package.json
└── tsconfig.json
```

## Guidelines

- TypeScript strict mode মেনে চলুন; `any` type এড়িয়ে চলুন
- Next.js App Router convention (`app/` directory) follow করুন
- Server Components default রাখুন; Client Components শুধু interactivity-র জন্য (`"use client"`)
- কোড লেখার সময় সহজ ও পরিষ্কার সমাধান বেছে নিন
- প্রজেক্টের existing convention মেনে চলুন
- অপ্রয়োজনীয় পরিবর্তন এড়িয়ে চলুন

## Notes

এই ফাইল Cursor AI-কে প্রজেক্ট সম্পর্কে context দেয়। প্রয়োজন অনুযায়ী এখানে rules, conventions, বা architecture notes যোগ করুন।
