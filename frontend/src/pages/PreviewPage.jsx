import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Edit3, Download, Eye, AlertTriangle } from 'lucide-react'
import 'katex/dist/katex.min.css'
import { InlineMath, BlockMath } from 'react-katex'
import toast from 'react-hot-toast'

import { getPreviewContent, updateBlockContent } from '../services/api'

const PreviewPage = () => {
  const { taskId } = useParams()
  const navigate = useNavigate()
  const [previewData, setPreviewData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [editingBlock, setEditingBlock] = useState(null)
  const [editText, setEditText] = useState('')

  useEffect(() => {
    loadPreviewData()
  }, [taskId])

  const loadPreviewData = async () => {
    try {
      const data = await getPreviewContent(taskId)
      setPreviewData(data)
    } catch (error) {
      console.error('載入預覽失敗:', error)
      toast.error('載入預覽失敗')
    } finally {
      setIsLoading(false)
    }
  }

  const handleEditBlock = (blockId, currentText) => {
    setEditingBlock(blockId)
    setEditText(currentText)
  }

  const handleSaveEdit = async () => {
    try {
      await updateBlockContent(taskId, editingBlock, editText)
      toast.success('修改已儲存')
      
      // 重新載入預覽
      await loadPreviewData()
      setEditingBlock(null)
      setEditText('')
    } catch (error) {
      toast.error('儲存失敗')
    }
  }

  const renderMathContent = (text, isInline = false) => {
    try {
      // 檢查是否包含 LaTeX 公式
      const latexPattern = /\$\$?(.*?)\$\$?/g
      const parts = []
      let lastIndex = 0
      let match

      while ((match = latexPattern.exec(text)) !== null) {
        // 添加公式前的文字
        if (match.index > lastIndex) {
          parts.push(text.slice(lastIndex, match.index))
        }

        // 添加公式
        const formula = match[1]
        if (match[0].startsWith('$$')) {
          // 區塊公式
          parts.push(<BlockMath key={match.index} math={formula} />)
        } else {
          // 行內公式
          parts.push(<InlineMath key={match.index} math={formula} />)
        }

        lastIndex = match.index + match[0].length
      }

      // 添加剩餘文字
      if (lastIndex < text.length) {
        parts.push(text.slice(lastIndex))
      }

      return parts.length > 1 ? parts : text
    } catch (error) {
      // 如果 LaTeX 渲染失敗，顯示原始文字
      return text
    }
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-success-600 bg-success-50'
    if (confidence >= 0.7) return 'text-warning-600 bg-warning-50'
    return 'text-error-600 bg-error-50'
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <Loader className="mx-auto h-12 w-12 text-blue-500 animate-spin" />
            <h2 className="mt-4 text-xl font-medium text-gray-900">載入預覽中...</h2>
          </div>
        </div>
      </div>
    )
  }

  if (!previewData) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <AlertTriangle className="mx-auto h-12 w-12 text-error-500" />
            <h2 className="mt-4 text-xl font-medium text-gray-900">載入失敗</h2>
            <button
              onClick={() => navigate('/upload')}
              className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              重新上傳
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">內容預覽與校對</h1>
          <p className="text-gray-600">檢查識別結果，可手動修正低信心區塊</p>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={() => navigate(`/export/${taskId}`)}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>匯出 Word</span>
          </button>
        </div>
      </div>

      {/* 處理統計 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="text-2xl font-bold text-gray-900">{previewData.total_blocks || 4}</div>
          <div className="text-sm text-gray-600">總區塊數</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="text-2xl font-bold text-success-600">{previewData.successful_blocks || 3}</div>
          <div className="text-sm text-gray-600">成功識別</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="text-2xl font-bold text-error-600">{previewData.failed_blocks || 1}</div>
          <div className="text-sm text-gray-600">需要修正</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="text-2xl font-bold text-blue-600">{previewData.processing_time || '4.2'}s</div>
          <div className="text-sm text-gray-600">處理時間</div>
        </div>
      </div>

      {/* 內容預覽 */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="border-b border-gray-200 px-6 py-4">
          <h3 className="text-lg font-medium text-gray-900">識別結果</h3>
          <p className="text-sm text-gray-600">低信心區塊以橘色標示，可點擊修正</p>
        </div>
        
        <div className="p-6 space-y-6">
          {/* 模擬預覽內容 */}
          <div className="space-y-4">
            {/* 題幹 */}
            <div className="border-l-4 border-blue-500 pl-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-2">題幹</h4>
                  <div className="text-gray-700 leading-relaxed">
                    {editingBlock === 'problem_1' ? (
                      <div className="space-y-3">
                        <textarea
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                          rows={3}
                        />
                        <div className="flex space-x-2">
                          <button
                            onClick={handleSaveEdit}
                            className="px-3 py-1 bg-success-600 text-white rounded text-sm hover:bg-success-700"
                          >
                            儲存
                          </button>
                          <button
                            onClick={() => setEditingBlock(null)}
                            className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
                          >
                            取消
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="relative">
                        <p>求解下列方程式：</p>
                        <div className="mt-2">
                          {renderMathContent("$$\\frac{x^2 + 2x + 1}{x - 1} = 0$$")}
                        </div>
                        
                        <button
                          onClick={() => handleEditBlock('problem_1', '求解下列方程式：$$\\frac{x^2 + 2x + 1}{x - 1} = 0$$')}
                          className="absolute top-0 right-0 p-1 text-gray-400 hover:text-gray-600"
                        >
                          <Edit3 className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
                
                <span className="ml-3 px-2 py-1 text-xs rounded-full bg-success-50 text-success-600">
                  信心度: 94%
                </span>
              </div>
            </div>

            {/* 選項 */}
            <div className="border-l-4 border-green-500 pl-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-2">選項</h4>
                  <div className="text-gray-700 space-y-1">
                    <p>(A) x = -1</p>
                    <p>(B) x = 1</p>
                    <p>(C) x = 0</p>
                    <p>(D) 無解</p>
                  </div>
                </div>
                
                <span className="ml-3 px-2 py-1 text-xs rounded-full bg-warning-50 text-warning-600">
                  信心度: 78%
                </span>
              </div>
            </div>

            {/* 詳解 */}
            <div className="border-l-4 border-purple-500 pl-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-2">詳解</h4>
                  <div className="text-gray-700 leading-relaxed space-y-2">
                    <p>由於分母不能為零，所以 {renderMathContent("$x \\neq 1$", true)}。</p>
                    <p>分子 {renderMathContent("$x^2 + 2x + 1 = (x + 1)^2 = 0$", true)}</p>
                    <p>因此 {renderMathContent("$x = -1$", true)}</p>
                    <p>答案是 (A)。</p>
                  </div>
                </div>
                
                <span className="ml-3 px-2 py-1 text-xs rounded-full bg-success-50 text-success-600">
                  信心度: 91%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 操作按鈕 */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={() => navigate('/upload')}
          className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          上傳新題目
        </button>
        
        <button
          onClick={() => navigate(`/export/${taskId}`)}
          className="px-8 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2"
        >
          <Download className="h-4 w-4" />
          <span>匯出 Word 文檔</span>
        </button>
      </div>

      {/* 低信心區塊提示 */}
      <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="h-5 w-5 text-warning-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-warning-800">
              校對提示
            </h4>
            <p className="text-sm text-warning-700 mt-1">
              橘色標示的區塊信心度較低，建議檢查並手動修正。公式識別錯誤可能影響 Word 匯出品質。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PreviewPage