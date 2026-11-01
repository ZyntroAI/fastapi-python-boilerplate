📧 Custom React Webmail (IMAP + SMTP Relay Version — No Inbound 25)
 
💡 Key Architecture Truth: Browser CANNOT directly open IMAP/SMTP TCP sockets → we build a Node.js API Proxy (runs inside Docker) that talks IMAP + SMTP relay; React only calls REST API; this is webmail client only (reads existing mailbox + sends via relay — NOT hosting mailboxes)
 
🏗️ Full Architecture Diagram
 
plaintext  
React Frontend ↔ Node.js API ↔ IMAP (993) / SMTP Relay (587)
✅ No inbound 25 required
✅ MX still points to your real mailbox provider
✅ Node receives credentials (or OAuth tokens) → connects to IMAP + Smarthost
⚠️ Production: Never store raw passwords; prefer OAuth2 / session only
 
 
📂 Full Project Structure
 
plaintext  
custom-webmail-relay/
├── docker-compose.yml
├── .env
├── backend/
│   ├── package.json
│   ├── src/
│   │   ├── server.ts
│   │   ├── imapService.ts
│   │   ├── smtpService.ts
│   │   └── types.ts
│   ├── tsconfig.json
│   └── Dockerfile.backend
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── InboxList.tsx
│   │   │   ├── EmailViewer.tsx
│   │   │   └── ComposeForm.tsx
│   │   ├── api.ts
│   │   └── main.tsx
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile.frontend
└── nginx/
    └── nginx.conf
 
 
🐳 docker-compose.yml (Relay‑Only)
 
yaml  
version: "3.8"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    container_name: webmail-backend
    restart: unless-stopped
    environment:
      TZ: Asia/Bangkok
      FRONTEND_URL: https://webmail.yourdomain.com
    expose:
      - "3000"
    networks:
      - webmailnet

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    container_name: webmail-frontend
    restart: unless-stopped
    expose:
      - "5173"
    networks:
      - webmailnet

  nginx:
    image: nginx:alpine
    container_name: webmail-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - backend
      - frontend
    networks:
      - webmailnet

networks:
  webmailnet:
    name: custom-webmail-network
 
 
💡 SSL: Use Traefik / Certbot instead of static certs for production; this compose does NOT auto‑issue certs
 
🖥️ Backend (Node + TypeScript + ImapFlow + Nodemailer)
 
backend/package.json
 
json  
{
  "name": "webmail-backend",
  "version": "1.0.0",
  "scripts": {
    "dev": "tsx src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js"
  },
  "dependencies": {
    "express": "^4.18.3",
    "imapflow": "^1.16.0",
    "nodemailer": "^6.9.10",
    "mailparser": "^3.6.5",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "tsx": "^4.0.0",
    "typescript": "^5.0.0",
    "@types/express": "^4.17.21",
    "@types/cors": "^2.8.17"
  }
}
 
 
backend/src/types.ts
 
ts  
export type MailboxConfig = {
  email: string;
  password: string;
  imapHost: string;
  imapPort: number;
  smtpHost: string;
  smtpPort: number;
};

export type EmailSummary = {
  uid: number;
  subject?: string;
  from?: string;
  date?: string;
};
 
 
backend/src/imapService.ts
 
ts  
import { ImapFlow } from "imapflow";
import { simpleParser } from "mailparser";
import type { MailboxConfig, EmailSummary } from "./types";

export async function listInbox(config: MailboxConfig): Promise<EmailSummary[]> {
  const client = new ImapFlow({
    host: config.imapHost,
    port: config.imapPort,
    secure: true,
    auth: { user: config.email, pass: config.password },
  });
  await client.connect();
  await client.mailboxOpen("INBOX");
  const lock = await client.getMailboxLock("INBOX");
  try {
    const messages: EmailSummary[] = [];
    for await (const msg of client.fetch("1:*", { envelope: true, uid: true })) {
      messages.push({
        uid: msg.uid,
        subject: msg.envelope?.subject,
        from: msg.envelope?.from?.[0]?.address,
        date: msg.envelope?.date?.toISOString(),
      });
    }
    return messages.reverse().slice(0,30);
  } finally {
    lock.release();
    await client.logout();
  }
}

export async function readEmail(config: MailboxConfig, uid: number) {
  const client = new ImapFlow({
    host: config.imapHost,
    port: config.imapPort,
    secure: true,
    auth: { user: config.email, pass: config.password },
  });
  await client.connect();
  await client.mailboxOpen("INBOX");
  const lock = await client.getMailboxLock("INBOX");
  try {
    const result = await client.fetchOne(uid, { source: true });
    return await simpleParser(result.source);
  } finally {
    lock.release();
    await client.logout();
  }
}
 
 
backend/src/smtpService.ts 
 
ts  
import nodemailer from "nodemailer";
import type { MailboxConfig } from "./types";

export async function sendViaRelay(config: MailboxConfig, to: string, subject: string, html: string) {
  const transporter = nodemailer.createTransport({
    host: config.smtpHost,
    port: config.smtpPort,
    secure: config.smtpPort === 465,
    auth: { user: config.email, pass: config.password },
  });
  return transporter.sendMail({
    from: config.email,
    to,
    subject,
    html,
  });
}
 
 
backend/src/server.ts
 
⚠️ Demo only: NO real session storage / encryption — credentials passed temporarily; production must add HTTPS + session + OAuth2 + never log passwords
 
ts  
import express from "express";
import cors from "cors";
import { listInbox, readEmail } from "./imapService";
import { sendViaRelay } from "./smtpService";
const app = express();
const port = 3000;

app.use(cors({ origin: process.env.FRONTEND_URL }));
app.use(express.json());

app.post("/api/inbox", async (req, res) => {
  try {
    const inbox = await listInbox(req.body);
    res.json(inbox);
  } catch (err) {
    res.status(401).json({error:"IMAP failed: check credentials / IMAP enable"});
  }
});

app.post("/api/email/:uid", async (req, res) => {
  try {
    const email = await readEmail(req.body, Number(req.params.uid));
    res.json({subject:email.subject,html:email.html,text:email.text});
  } catch (err) {
    res.status(400).json({error:"Failed reading email"});
  }
});

app.post("/api/send", async (req, res) => {
  try {
    await sendViaRelay(req.body, req.body.to, req.body.subject, req.body.html);
    res.json({ok:true});
  } catch (err) {
    res.status(400).json({error:"SMTP Relay failed"});
  }
});

app.listen(port, ()=>console.log(`Backend running ${port}`));
 
 
backend/Dockerfile.backend
 
dockerfile  
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm","start"]
 
 
⚛️ Frontend (Vite + React + TypeScript)
 
frontend/package.json
 
json  
{
  "name": "webmail-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview --port 5173 --host"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
 
 
frontend/vite.config.ts
 
ts  
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins:[react()],
  server:{host:true,port:5173}
})
 
 
frontend/src/api.ts
 
ts  
const API_URL = "/api";
export type LoginData = {
  email:string;password:string;imapHost:string;imapPort:number;smtpHost:string;smtpPort:number;
};

export async function fetchInbox(creds:LoginData){
  const res = await fetch(`${API_URL}/inbox`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(creds)});
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function fetchEmail(creds:LoginData,uid:number){
  const res = await fetch(`${API_URL}/email/${uid}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(creds)});
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function sendEmail(creds:LoginData,to:string,subject:string,html:string){
  const res = await fetch(`${API_URL}/send`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({...creds,to,subject,html})});
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}
 
 
frontend/src/App.tsx
 
tsx  
import React, { useState } from 'react';
import LoginForm from './components/LoginForm';
import InboxList from './components/InboxList';
import EmailViewer from './components/EmailViewer';
import ComposeForm from './components/ComposeForm';
import type { LoginData } from './api';

function App(){
  const [creds,setCreds] = useState<LoginData|null>(null);
  const [selectedUid,setSelectedUid] = useState<number|null>(null);
  const [viewMode,setViewMode] = useState<'inbox'|'compose'>('inbox');
  if(!creds) return <LoginForm onLogin={setCreds}/>;
  return (
    <main style={{maxWidth:"1100px",margin:"0 auto",padding:"20px"}}>
      <nav>
        <button onClick={()=>setViewMode('inbox')}>📥 Inbox</button>
        <button onClick={()=>setViewMode('compose')}>✍️ Compose</button>
        <button onClick={()=>{setCreds(null);setSelectedUid(null);}}>🚪 Logout</button>
      </nav>
      {viewMode === 'inbox' && selectedUid === null && <InboxList creds={creds} onSelect={setSelectedUid}/>}
      {viewMode === 'inbox' && selectedUid !== null && <EmailViewer creds={creds} uid={selectedUid} onBack={()=>setSelectedUid(null)}/>}
      {viewMode === 'compose' && <ComposeForm creds={creds}/>}
    </main>
  );
}
export default App;
 
 
frontend/src/components/LoginForm.tsx
 
tsx  
import React,{useState} from 'react';
import type {LoginData} from '../api';
type Props = {onLogin:(data:LoginData)=>void};
export default function LoginForm({onLogin}:Props){
  const [form,setForm]=useState<LoginData>({
    email:"you@yourdomain.com",password:"",imapHost:"imap.yourmail.com",imapPort:993,smtpHost:"smtp.yourrelay.com",smtpPort:587
  });
  return (
    <div style={{maxWidth:"500px",margin:"40px auto"}}>
      <h2>🔐 Login to Mailbox</h2>
      <input placeholder="Email" value={form.email} onChange={(e)=>setForm({...form,email:e.target.value})}/><br/>
      <input placeholder="Password / App Password" type="password" value={form.password} onChange={(e)=>setForm({...form,password:e.target.value})}/><br/>
      <input placeholder="IMAP Host" value={form.imapHost} onChange={(e)=>setForm({...form,imapHost:e.target.value})}/><br/>
      <input placeholder="IMAP Port" type="number" value={form.imapPort} onChange={(e)=>setForm({...form,imapPort:Number(e.target.value)})}/><br/>
      <input placeholder="SMTP Relay Host" value={form.smtpHost} onChange={(e)=>setForm({...form,smtpHost:e.target.value})}/><br/>
      <input placeholder="SMTP Relay Port" type="number" value={form.smtpPort} onChange={(e)=>setForm({...form,smtpPort:Number(e.target.value)})}/><br/>
      <button onClick={()=>onLogin(form)}>Login</button>
    </div>
  );
}
 
 
frontend/src/components/InboxList.tsx
 
tsx  
import React,{useState,useEffect} from 'react';
import {fetchInbox} from '../api';
import type {LoginData} from '../api';
type Props={creds:LoginData;onSelect:(uid:number)=>void};
export default function InboxList({creds,onSelect}:Props){
  const [list,setList]=useState<any[]>([]);
  const [loading,setLoading]=useState(true);
  useEffect(()=>{
    fetchInbox(creds).then(setList).catch(console.error).finally(()=>setLoading(false));
  },[creds]);
  if(loading) return <p>Loading inbox...</p>;
  return (
    <div>
      <h2>📥 Inbox</h2>
      {list.map((item)=>(
        <div key={item.uid} onClick={()=>onSelect(item.uid)} style={{border:"1px solid #ccc",padding:"10px",margin:"8px",cursor:"pointer"}}>
          <strong>{item.subject || "(No Subject)"}</strong>
          <p>{item.from} • {item.date?.slice(0,10)}</p>
        </div>
      ))}
    </div>
  );
}
 
 
frontend/src/components/EmailViewer.tsx
 
tsx  
import React,{useState,useEffect} from 'react';
import {fetchEmail} from '../api';
import type {LoginData} from '../api';
type Props={creds:LoginData;uid:number;onBack:()=>void};
export default function EmailViewer({creds,uid,onBack}:Props){
  const [email,setEmail]=useState<any>(null);
  useEffect(()=>{fetchEmail(creds,uid).then(setEmail).catch(console.error);},[creds,uid]);
  return (
    <div>
      <button onClick={onBack}>← Back</button>
      <h2>{email?.subject}</h2>
      <div dangerouslySetInnerHTML={{__html:email?.html || email?.text}}></div>
    </div>
  );
}
 
 
frontend/src/components/ComposeForm.tsx
 
tsx  
import React,{useState} from 'react';
import {sendEmail} from '../api';
import type {LoginData} from '../api';
type Props={creds:LoginData};
export default function ComposeForm({creds}:Props){
  const [to,setTo]=useState("");
  const [subject,setSubject]=useState("");
  const [html,setHtml]=useState("");
  const [status,setStatus]=useState("");
  async function handleSend(){
    try{
      await sendEmail(creds,to,subject,html);
      setStatus("✅ Sent successfully via relay");
    }catch(err){setStatus("❌ Failed sending");}
  }
  return (
    <div>
      <h2>✍️ Compose</h2>
      <input placeholder="To" value={to} onChange={(e)=>setTo(e.target.value)}/><br/>
      <input placeholder="Subject" value={subject} onChange={(e)=>setSubject(e.target.value)}/><br/>
      <textarea placeholder="Message HTML" rows={10} value={html} onChange={(e)=>setHtml(e.target.value)}></textarea><br/>
      <button onClick={handleSend}>Send via Relay</button>
      <p>{status}</p>
    </div>
  );
}
 
 
frontend/src/main.tsx
 
tsx  
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
ReactDOM.createRoot(document.getElementById('root')!).render(<App/>);
 
 
frontend/index.html
 
html  
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Custom Webmail Relay</title></head>
<body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body>
</html>
 
 
nginx/nginx.conf
 
nginx  
events {}
http {
  server {
    listen 80;
    server_name webmail.yourdomain.com;
    return 301 https://$host$request_uri;
  }
  server {
    listen 443 ssl;
    server_name webmail.yourdomain.com;
    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    location /api {
      proxy_pass http://backend:3000;
      proxy_set_header Host $host;
    }
    location / {
      proxy_pass http://frontend:5173;
      proxy_set_header Host $host;
    }
  }
}
 
 
🚀 Deployment Steps
 
bash  
#1 Create folders
mkdir -p custom-webmail-relay/certs
cd custom-webmail-relay

#2 Build containers
docker compose build

#3 Get SSL cert (Certbot example)
sudo certbot certonly --standalone -d webmail.yourdomain.com
sudo cp