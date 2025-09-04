import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { Toaster } from 'react-hot-toast'

// 頁面組件
import HomePage from './pages/HomePage'
import UploadPage from './pages/UploadPage' 
import ProcessingPage from './pages/ProcessingPage'
import PreviewPage from './pages/PreviewPage'
import ExportPage from './pages/ExportPage'
import ManagementPage from './pages/ManagementPage'

// 佈局組件
import Layout from './components/Layout'

// 建立 React Query 客戶端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5分鐘
      cacheTime: 10 * 60 * 1000, // 10分鐘
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/processing/:taskId" element={<ProcessingPage />} />
            <Route path="/preview/:taskId" element={<PreviewPage />} />
            <Route path="/export/:taskId" element={<ExportPage />} />
            <Route path="/management" element={<ManagementPage />} />
          </Routes>
        </Layout>
      </Router>
      
      {/* 全域通知 */}
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
            fontSize: '14px',
          },
          success: {
            style: {
              background: '#22c55e',
            },
          },
          error: {
            style: {
              background: '#ef4444',
            },
          },
        }}
      />
    </QueryClientProvider>
  )
}

export default App