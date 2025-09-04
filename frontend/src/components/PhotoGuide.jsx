import React from 'react'
import { X, Camera, CheckCircle, XCircle } from 'lucide-react'

const PhotoGuide = ({ onClose }) => {
  const goodExamples = [
    {
      title: '清晰正拍',
      description: '光線充足，角度垂直，文字清晰可見',
      tips: ['使用自然光或充足室內光', '手機與紙面平行', '避免陰影遮擋']
    },
    {
      title: '單題完整',
      description: '包含完整題目，題號、題幹、選項都在畫面內',
      tips: ['確保題目邊界完整', '預留適當邊距', '避免裁切重要內容']
    },
    {
      title: '高解析度',
      description: '圖片清晰度足夠，文字和公式都能清楚辨識',
      tips: ['使用手機最高解析度', '避免過度數位變焦', '距離適中拍攝']
    }
  ]

  const badExamples = [
    {
      title: '模糊不清',
      description: '手震、對焦不準或解析度過低',
      solution: '使用三腳架或穩定手機，確保對焦清晰'
    },
    {
      title: '角度傾斜',
      description: '拍攝角度過斜，造成文字變形',
      solution: '保持手機與紙面平行，使用網格線輔助'
    },
    {
      title: '光線不足',
      description: '過暗或光線不均，影響識別準確度',
      solution: '使用充足光源，避免陰影和反光'
    },
    {
      title: '多題混合',
      description: '一張圖片包含多個題目',
      solution: '分別拍攝每個題目，或使用裁切工具'
    }
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-100 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-xl font-medium text-gray-900 flex items-center space-x-2">
            <Camera className="h-6 w-6" />
            <span>拍攝建議</span>
          </h3>
          
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6 overflow-auto max-h-[calc(90vh-120px)]">
          <div className="space-y-8">
            {/* 良好示例 */}
            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-success-500" />
                <span>建議做法</span>
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {goodExamples.map((example, index) => (
                  <div key={index} className="border border-success-200 rounded-lg p-4 bg-success-50">
                    <h5 className="font-medium text-success-800 mb-2">{example.title}</h5>
                    <p className="text-sm text-success-700 mb-3">{example.description}</p>
                    <ul className="text-xs text-success-600 space-y-1">
                      {example.tips.map((tip, tipIndex) => (
                        <li key={tipIndex} className="flex items-start space-x-1">
                          <span className="text-success-500 mt-0.5">•</span>
                          <span>{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            {/* 避免事項 */}
            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center space-x-2">
                <XCircle className="h-5 w-5 text-error-500" />
                <span>避免事項</span>
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {badExamples.map((example, index) => (
                  <div key={index} className="border border-error-200 rounded-lg p-4 bg-error-50">
                    <h5 className="font-medium text-error-800 mb-2">{example.title}</h5>
                    <p className="text-sm text-error-700 mb-3">{example.description}</p>
                    <div className="text-xs text-error-600">
                      <span className="font-medium">解決方案: </span>
                      {example.solution}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 技術規格 */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">技術規格建議</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 className="font-medium text-gray-800 mb-2">影像規格</h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• 解析度: 至少 1200×800 像素</li>
                    <li>• 格式: JPG, PNG, WebP</li>
                    <li>• 檔案大小: 小於 50MB</li>
                    <li>• 色彩: 彩色或灰階皆可</li>
                  </ul>
                </div>
                
                <div>
                  <h5 className="font-medium text-gray-800 mb-2">拍攝環境</h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• 光線: 自然光或白色 LED 燈</li>
                    <li>• 背景: 單純背景，避免干擾</li>
                    <li>• 距離: 30-50 公分拍攝距離</li>
                    <li>• 穩定: 使用三腳架或穩定手持</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* 公式拍攝特別提醒 */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-800 mb-2">數學公式特別提醒</h4>
              <div className="text-sm text-blue-700 space-y-1">
                <p>• 確保分數線、根號、積分號等符號完整清晰</p>
                <p>• 上下標文字不能過小或模糊</p>
                <p>• 複雜公式建議單獨拍攝，避免與文字混合</p>
                <p>• 手寫公式請確保筆跡工整，字體大小適中</p>
              </div>
            </div>
          </div>
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            知道了
          </button>
        </div>
      </div>
    </div>
  )
}

export default PhotoGuide