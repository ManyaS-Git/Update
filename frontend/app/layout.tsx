import type { Metadata } from "next";
import "./globals.css";
import "./carousel.css";
import "./pages.css";
export const metadata:Metadata={title:{default:"UPDATES — Social Intelligence",template:"%s | UPDATES"},description:"AI-powered social intelligence and narrative analytics, backed by evidence and confidence."};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
