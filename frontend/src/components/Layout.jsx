import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FileText, Upload, Settings, BarChart3 } from 'lucide-react'

const Layout = ({ children }) => {
  const location = useLocation()
  
  const navigation = [
    { name: '首頁', href: '/', icon: FileText },
    { name: '上傳', href: '/upload', icon: Upload },
    { name: '管理', href: '/management', icon: BarChart3 },
  ]
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* 導航欄 */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <FileText className="h-8 w-8 text-primary-600" />
                <span className="text-xl font-bold text-gray-900">
                  OCR 題解系統
                </span>
              </Link>
            </div>
            
            {/* 導航選單 */}
            <div className="flex items-center space-x-8">
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.href
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'text-primary-600 bg-primary-50'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </div>
          </div>
        </div>
      </nav>
      
      {/* 主內容區 */}
      <main className="flex-1 max-w-7xl w-full mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
      
      {/* 頁腳 */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-600">
            © 2024 OCR 數學題目解析系統. 支援多種 OCR 引擎與 Word 匯出.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout