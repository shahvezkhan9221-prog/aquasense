import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"
import "./globals.css"

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" })
const mono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono" })

export const metadata: Metadata = { title: "JalSetu | Water Intelligence", description: "Real-time village water quality monitoring across Northeast India." }

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="bg-background" suppressHydrationWarning>
      <body className={`${geist.variable} ${mono.variable}`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false} disableTransitionOnChange>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
