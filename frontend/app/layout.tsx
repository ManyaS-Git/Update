import type { Metadata } from "next";
import "./globals.css";
import "./carousel.css";
export const metadata:Metadata={title:{default:"UPDATES — Social Intelligence",template:"%s | UPDATES"},description:"AI-powered social intelligence and narrative analytics, backed by evidence and confidence."};
const themeScript=`try{document.documentElement.dataset.theme=localStorage.getItem("updates-theme")==="dark"?"dark":"light"}catch{document.documentElement.dataset.theme="light"}`;
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en" suppressHydrationWarning><head><script dangerouslySetInnerHTML={{__html:themeScript}}/></head><body>{children}</body></html>}
