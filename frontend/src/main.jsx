import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import '@uiw/react-md-editor/markdown-editor.css';
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
