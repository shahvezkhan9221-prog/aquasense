"use client"

import { useEffect, useRef, useState } from "react"
import { useChat } from "@ai-sdk/react"
import { Loader2, MessageCircle, Send, Sparkles, X } from "lucide-react"

const suggestions = [
  "What causes cholera in drinking water?",
  "What does HIGH risk mean here?",
  "How do I make water safe to drink?",
  "What is a safe turbidity level?",
]

export function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState("")
  const { messages, sendMessage, status, error } = useChat()
  const listRef = useRef<HTMLDivElement>(null)
  const isLoading = status === "submitted" || status === "streaming"

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight
  }, [messages, open])

  const submit = (text: string) => {
    if (!text.trim() || isLoading) return
    sendMessage({ text })
    setInput("")
  }

  return (
    <div className="chat-widget">
      {open && (
        <div className="chat-panel" role="dialog" aria-label="JalSetu help chat">
          <div className="chat-panel-header">
            <div className="flex items-center gap-2.5">
              <div className="chat-avatar"><Sparkles className="size-4" /></div>
              <div>
                <div className="text-sm font-semibold leading-tight">JalSetu Help</div>
                <div className="text-[11px] leading-tight text-muted-foreground">Ask about water safety &amp; diseases</div>
              </div>
            </div>
            <button className="icon-button" onClick={() => setOpen(false)} aria-label="Close chat"><X /></button>
          </div>

          <div className="chat-messages" ref={listRef}>
            {messages.length === 0 && (
              <div className="chat-empty">
                <p className="text-sm text-muted-foreground">
                  Hi, I&apos;m Neer. Ask me anything about water-borne diseases, safe drinking water, or how to read your risk dashboard.
                </p>
                <div className="mt-4 flex flex-col gap-2">
                  {suggestions.map((s) => (
                    <button key={s} className="chat-suggestion" onClick={() => submit(s)}>{s}</button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((message) => (
              <div key={message.id} className={`chat-bubble-row ${message.role === "user" ? "is-user" : "is-assistant"}`}>
                <div className="chat-bubble">
                  {message.parts.map((part, i) => part.type === "text" ? <span key={`${message.id}-${i}`}>{part.text}</span> : null)}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="chat-bubble-row is-assistant">
                <div className="chat-bubble chat-bubble-loading"><Loader2 className="size-3.5 animate-spin" /> Thinking…</div>
              </div>
            )}
            {status === "error" && (
              <div className="chat-bubble-row is-assistant">
                <div className="chat-bubble chat-error-bubble">
                  {error?.message?.includes("credit card")
                    ? "The AI Gateway needs a credit card on file before it can respond. Ask the site owner to add one in the Vercel AI Gateway settings."
                    : "Something went wrong reaching Neer. Please try again in a moment."}
                </div>
              </div>
            )}
          </div>

          <form
            className="chat-input-row"
            onSubmit={(e) => {
              e.preventDefault()
              submit(input)
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question…"
              className="chat-input"
              aria-label="Message"
            />
            <button type="submit" className="chat-send" disabled={!input.trim() || isLoading} aria-label="Send message">
              <Send className="size-4" />
            </button>
          </form>
        </div>
      )}

      <button className="chat-launcher" onClick={() => setOpen((v) => !v)} aria-label={open ? "Close help chat" : "Open help chat"}>
        {open ? <X /> : <MessageCircle />}
      </button>
    </div>
  )
}
