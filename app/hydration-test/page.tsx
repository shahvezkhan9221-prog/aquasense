"use client"

import { useState } from "react"

export default function HydrationTest() {
  const [count, setCount] = useState(0)
  return (
    <div style={{ padding: 40, fontSize: 24 }}>
      <p>Count: {count}</p>
      <button onClick={() => setCount((c) => c + 1)} style={{ padding: 12, fontSize: 20 }}>
        Increment
      </button>
    </div>
  )
}
