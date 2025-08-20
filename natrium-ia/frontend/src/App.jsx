import React, { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function Message({ role, text }){
  const isUser = role === 'user'
  return (
    <div className={`w-full flex ${isUser ? 'justify-end' : 'justify-start'} my-2`}>
      <div className={`max-w-[75%] rounded-2xl px-4 py-2 shadow ${isUser ? 'bg-blue-600 text-white' : 'bg-white border'}`}>
        {text}
      </div>
    </div>
  )
}

export default function App(){
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [customerId, setCustomerId] = useState('demo-customer')

  async function sendMessage(e){
    e.preventDefault()
    if(!text && !file) return

    let uploadedUrl = null
    if(file){
      const fd = new FormData()
      fd.append('file', file)
      const up = await fetch(`${API_BASE}/upload`, { method: 'POST', body: fd })
      const upRes = await up.json()
      uploadedUrl = upRes.file_url
      setFile(null)
    }

    const myMsg = { role: 'user', text: text || (uploadedUrl ? `Enviei um arquivo: ${uploadedUrl}` : '') }
    setMessages(m => [...m, myMsg])
    setText('')

    const payload = {
      customer_id: customerId,
      text: myMsg.text,
      agent: null,
      order_id: null
    }
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await res.json()
    setMessages(m => [...m, { role: 'assistant', text: data.reply }])
  }

  return (
    <div className="h-full flex flex-col">
      <header className="border-b bg-white py-3 px-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold">Natrium IA – Atendimento</h1>
        <div className="text-sm opacity-70">Cliente: 
          <input className="ml-2 border rounded px-2 py-1" value={customerId} onChange={e=>setCustomerId(e.target.value)} />
        </div>
      </header>
      <main className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-10">
            Envie uma mensagem ou anexe a receita (imagem/PDF) para começar.
          </div>
        )}
        {messages.map((m, i) => <Message key={i} role={m.role} text={m.text} />)}
      </main>
      <form onSubmit={sendMessage} className="p-3 bg-white border-t flex gap-2">
        <input
          value={text}
          onChange={e=>setText(e.target.value)}
          placeholder="Digite sua mensagem..."
          className="flex-1 border rounded-2xl px-4 py-2"
        />
        <input type="file" onChange={e=>setFile(e.target.files?.[0] || null)} />
        <button className="px-4 py-2 rounded-2xl bg-blue-600 text-white">Enviar</button>
      </form>
    </div>
  )
}
