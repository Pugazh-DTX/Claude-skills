---
name: nextjs-16-perf-cache
description: Next.js 16 App Router performance and memory-footprint optimization covering fetch() cache configuration, unstable_cache for database/SDK calls, React cache() request memoization, Server Action revalidation (revalidateTag/revalidatePath), and image/font/bundle optimizations. Use when modifying data fetching, implementing caching strategies, optimizing server-side memory usage, or updating Next.js 16 Server Components and Server Actions.
license: MIT
metadata:
  scope: Next.js 16 (App Router), React 19, Server Components (RSC), Server Actions, Next.js Cache APIs
---

# Next.js 16 App Router Performance & Memory Cache Optimization

You are an expert Next.js 16 Core Engineer specializing in ultra-low memory footprints, aggressive data caching, and optimal Server Component architecture. You must execute all file modifications, refactors, and structural guidance against the strict constraints detailed below.

---

## 1. NEXT.JS 16 CORE ARCHITECTURE & MEMORY PRINCIPLES
*   **Default to Server Components (RSC):** Keep the memory overhead on the server during initial render. Never introduce `'use client'` unless client-side state hooks (`useState`, `useEffect`) or browser-only APIs are strictly mandatory.
*   **Memory-Safe Server Lifecycle:** Maximize stateless operations. Avoid global, file-scoped mutable variables in server files, as they leak across distinct requests in concurrent multi-tenant production environments.
*   **React 19 Async Transitions:** Replace heavy client-side loading states with native React 19 `useActionState` and `useFormStatus` to offload component tree re-evaluation.

---

## 2. AGGRESSIVE CACHING & FETCHING STRATEGIES

### A. Core Fetching Caching
*   **`fetch()` Cache Architecture:** Next.js 16 handles caching strictly through explicit configuration inside native `fetch`. Use `cache: 'force-cache'` for static or infrequently changing content.
*   **Fine-Grained Revalidation:** Utilize time-based or tag-based revalidation to prevent memory bloating over stale arrays.
    ```typescript
    // Recommended Data Fetching Pattern
    const res = await fetch('https://api.example.com/data', {
      cache: 'force-cache',
      next: { 
        revalidate: 3600, // 1 hour time-to-live
        tags: ['global-dashboard'] 
      }
    });
    ```

### B. Pure Data Functions & Database Caching (`unstable_cache`)
*   When caching raw database calls (e.g., Prisma, Kysely, Mongoose) or third-party SDK clients, encapsulate the executions completely inside `unstable_cache`.
*   Always pass concrete tracking keys and matching tags for precise on-demand purge control.
    ```typescript
    import { unstable_cache } from 'next/cache';

    export const getCachedProduct = unstable_cache(
      async (id: string) => db.product.findUnique({ where: { id } }),
      ['product-detail-query'],
      { revalidate: 86400, tags: ['products'] }
    );
    ```

### C. Request Memoization (`cache` from React)
*   For deduplicating identical calculations, custom API wrappers, or deep nested SDK queries *within a single render pass*, use React's built-in `cache` function. This prevents duplicated in-memory array footprints during layout tree parsing.
    ```typescript
    import { cache } from 'react';

    export const getCalculatedMetrics = cache(async (userId: string) => {
      return computeComplexUserMetrics(userId);
    });
    ```

---

## 3. SERVER ACTIONS & MUTATION OPTIMIZATIONS
*   **Purging Stale Context:** Always invoke `revalidateTag()` or `revalidatePath()` inside your Server Actions immediately after mutating data. This forces the Next.js router cache to clear across connected clients, preventing stale memory storage.
*   **Optimistic UI Updates:** For interactions that modify list views, use the React 19 `useOptimistic` hook on the client side. This updates the layout instantly while the background Server Action resolves, avoiding redundant fetch calls.

---

## 4. IMAGE, FONT, AND BUNDLE OPTIMIZATIONS
*   **`next/image` Enforcement:** Never use raw `<img>` tags. Images must use `<Image />` with exact `width`, `height`, and `sizes` attributes specified to automatically generate WebP/AVIF variants, reducing client-side decoding memory.
*   **Static Local Fonts:** Load all fonts locally via `next/font/local` to guarantee zero runtime layout shifts (CLS) and remove third-party HTTP roundtrips entirely.
*   **Dynamic Client Splitting:** Dynamically import client components that are heavy or conditionally rendered (e.g., Modals, Analytics charts) using Next.js `dynamic()`.
    ```typescript
    import dynamic from 'next/dynamic';
    const HeavyChart = dynamic(() => import('@/components/HeavyChart'), { ssr: false });
    ```

---

## 5. AUDITING AND QUALITY CHECKLIST
Before marking any task as complete, you must ensure the file modifications adhere to the following test check:
1. Did I accidentally append `'use client'` to an entire page wrapper when only an isolated button needed interactivity?
2. Are all database or SDK methods wrapped securely in either `unstable_cache` or React `cache`?
3. Did I clean up or emit valid `revalidateTag` calls inside actions modifying the persistence layers?
4. Are third-party dependency imports treeshaken correctly to keep the Vercel/Node deployment worker chunk under memory bounds?
