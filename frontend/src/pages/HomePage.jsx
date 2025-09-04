import React from 'react'
import { Link } from 'react-router-dom'
import { Upload, FileText, Zap, CheckCircle, ArrowRight } from 'lucide-react'

const HomePage = () => {
  const features = [
    {
      icon: Upload,
      title: '智慧上傳',
      description: '支援圖片和 PDF，自動檢測多題並建議裁切',
      details: ['拖拽上傳', '格式驗證', '多題檢測', '裁切工具']
    },
    {
      icon: Zap,
      title: '雙引擎 OCR',
      description: '文字和公式分別使用專門引擎，置信度檢查與自動重試',
      details: ['PaddleOCR 中文', 'pix2tex 公式', '備援引擎', 'Mathpix 兜底']
    },
    {
      icon: FileText,
      title: 'Word 匯出',
      description: '生成包含 OMML 公式的 Word 文檔，可直接編輯',
      details: ['OMML 公式', '自訂字級', '圖片原位', '段落樣式']
    }
  ]

  const workflow = [
    { step: 1, title: '上傳圖片', description: '拖拽或選擇題目圖片' },
    { step: 2, title: 'OCR 識別', description: '自動識別文字與公式' },
    { step: 3, title: '預覽校對', description: '檢查結果並手動修正' },
    { step: 4, title: '匯出 Word', description: '下載包含 OMML 公式的文檔' }
  ]

  return (
    <div className="space-y-12">
      {/* Hero 區塊 */}
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl">
          OCR 數學題目
          <span className="text-primary-600">解析系統</span>
        </h1>
        
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          上傳物理/數學題目圖片，自動識別文字與公式，匯出包含可編輯 OMML 公式的 Word 文檔
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/upload"
            className="px-8 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center space-x-2"
          >
            <Upload className="h-5 w-5" />
            <span>開始上傳</span>
          </Link>
          
          <Link
            to="/management"
            className="px-8 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            查看統計
          </Link>
        </div>
      </div>

      {/* 功能特色 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {features.map((feature, index) => {
          const Icon = feature.icon
          return (
            <div key={index} className="bg-white rounded-lg shadow-sm p-6 border">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <Icon className="h-6 w-6 text-primary-600" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">{feature.title}</h3>
              </div>
              
              <p className="text-gray-600 mb-4">{feature.description}</p>
              
              <ul className="space-y-1">
                {feature.details.map((detail, detailIndex) => (
                  <li key={detailIndex} className="flex items-center space-x-2 text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-success-500 flex-shrink-0" />
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>
          )
        })}
      </div>

      {/* 工作流程 */}
      <div className="bg-white rounded-lg shadow-sm p-8">
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
          簡單四步驟
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {workflow.map((item, index) => (
            <div key={index} className="text-center">
              <div className="flex items-center justify-center mb-4">
                <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  {item.step}
                </div>
                {index < workflow.length - 1 && (
                  <ArrowRight className="h-5 w-5 text-gray-400 ml-4 hidden md:block" />
                )}
              </div>
              
              <h3 className="font-medium text-gray-900 mb-2">{item.title}</h3>
              <p className="text-sm text-gray-600">{item.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 技術規格 */}
      <div className="bg-gray-50 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
          技術規格
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-center">
          <div>
            <div className="text-2xl font-bold text-primary-600">≥ 95%</div>
            <div className="text-sm text-gray-600">單題成功率</div>
          </div>
          
          <div>
            <div className="text-2xl font-bold text-primary-600">≤ 6s</div>
            <div className="text-sm text-gray-600">平均處理時間</div>
          </div>
          
          <div>
            <div className="text-2xl font-bold text-primary-600">≤ 5%</div>
            <div className="text-sm text-gray-600">兜底觸發率</div>
          </div>
          
          <div>
            <div className="text-2xl font-bold text-primary-600">≥ 98%</div>
            <div className="text-sm text-gray-600">LaTeX 可編譯率</div>
          </div>
        </div>
      </div>

      {/* 支援格式 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-medium text-gray-900 text-center mb-6">
          支援格式與規格
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h4 className="font-medium text-gray-800 mb-3">輸入格式</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• 圖片: JPG, PNG, WebP</li>
              <li>• 文檔: PDF (自動分頁)</li>
              <li>• 大小: 最大 50MB</li>
              <li>• 解析度: 建議 ≥ 1200×800</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-800 mb-3">輸出格式</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Word 文檔 (.docx)</li>
              <li>• OMML 原生公式（可編輯）</li>
              <li>• 自訂段落樣式</li>
              <li>• 圖片原位插入</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage