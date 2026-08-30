"use client";
import Link from "next/link";
export default function ErrorPage({reset}:{reset:()=>void}){return <main className="route-error"><span>Analytics unavailable</span><h1>We couldn’t load this topic.</h1><p>The page is ready for dynamic data, but the analytics service did not return a usable response.</p><div><button onClick={reset}>Try again</button><Link href="/">Return home</Link></div></main>}
