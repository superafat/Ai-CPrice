import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Download, Settings, Eye, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import { InlineMath, BlockMath } from 'react-katex'

import { exportToWord, getExportSettings } from '../services/api'

const ExportPage = () => {
  const { taskId } = useParams()
  const [exportSettings, setExportSettings] = useState({
    problem_font_size: 11,
    solution_font_size: 9,
    include_figure_captions: true,
    image_max_width_cm: 14.0,
    maintain_aspect_ratio: true,
    anchor_images_inline: true
  })
  const [isExporting, setIsExporting] = useState(false)
  const [previewMode, setPreviewMode] = useState(true)
  const [exportResult, setExportResult] = useState(null)

  useEffect(() => {
    loadDefaultSettings()
  }, [])

  const loadDefaultSettings = async () => {
    try {
      const settings = await getExportSettings()
      setExportSettings(settings)
    } catch (error) {
      console.error('載入設定失敗:', error)
    }
  }

  const handleExport = async () => {
    setIsExporting(true)
    
    try {
      const result = await exportToWord(taskId, exportSettings)
      setExportResult(result)
      toast.success('Word 文檔匯出成功！')
    } catch (error) {
      console.error('匯出失敗:', error)
      toast.error('匯出失敗，請重試')
    } finally {
      setIsExporting(false)
    }
  }

  const handleDownload = () => {
    if (exportResult?.output_file) {
      const downloadUrl = `/api/export/download/${taskId}`
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `problem_solution_${taskId}.docx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const updateFontSize = (type, size) => {
    setExportSettings(prev => ({
      ...prev,
      [type]: size
    }))
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* 頁面標題 */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900">匯出設定</h1>
        <p className="text-gray-600">調整字體大小與版面設定，即時預覽效果</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 設定面板 */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <span>匯出設定</span>
            </h3>

            {/* 字體大小設定 */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  題幹/選項字級 (pt)
                </label>
                <div className="flex items-center space-x-3">
                  <input
                    type="range"
                    min="8"
                    max="16"
                    step="1"
                    value={exportSettings.problem_font_size}
                    onChange={(e) => updateFontSize('problem_font_size', parseInt(e.target.value))}
                    className="flex-1"
                  />
                  <span className="w-8 text-sm font-medium text-gray-900">
                    {exportSettings.problem_font_size}
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  詳解字級 (pt)
                </label>
                <div className="flex items-center space-x-3">
                  <input
                    type="range"
                    min="8"
                    max="16"
                    step="1"
                    value={exportSettings.solution_font_size}
                    onChange={(e) => updateFontSize('solution_font_size', parseInt(e.target.value))}
                    className="flex-1"
                  />
                  <span className="w-8 text-sm font-medium text-gray-900">
                    {exportSettings.solution_font_size}
                  </span>
                </div>
              </div>
            </div>

            {/* 圖片設定 */}
            <div className="mt-6 space-y-4">
              <h4 className="font-medium text-gray-900">圖片設定</h4>
              
              <div className="flex items-center justify-between">
                <label className="text-sm text-gray-700">包含圖片說明</label>
                <input
                  type="checkbox"
                  checked={exportSettings.include_figure_captions}
                  onChange={(e) => setExportSettings(prev => ({
                    ...prev,
                    include_figure_captions: e.target.checked
                  }))}
                  className="rounded"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  圖片最大寬度 (cm)
                </label>
                <input
                  type="number"
                  min="5"
                  max="20"
                  step="0.5"
                  value={exportSettings.image_max_width_cm}
                  onChange={(e) => setExportSettings(prev => ({
                    ...prev,
                    image_max_width_cm: parseFloat(e.target.value)
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            {/* 匯出按鈕 */}
            <div className="mt-6 space-y-3">
              <button
                onClick={handleExport}
                disabled={isExporting}
                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                  isExporting
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-primary-600 text-white hover:bg-primary-700'
                }`}
              >
                {isExporting ? '匯出中...' : '匯出 Word 文檔'}
              </button>

              {exportResult && (
                <button
                  onClick={handleDownload}
                  className="w-full py-3 px-4 bg-success-600 text-white rounded-lg hover:bg-success-700 flex items-center justify-center space-x-2"
                >
                  <Download className="h-4 w-4" />
                  <span>下載文檔</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* 預覽區域 */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm">
            <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900 flex items-center space-x-2">
                <Eye className="h-5 w-5" />
                <span>即時預覽</span>
              </h3>
              
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>題幹: {exportSettings.problem_font_size}pt</span>
                <span>|</span>
                <span>詳解: {exportSettings.solution_font_size}pt</span>
              </div>
            </div>
            
            <div className="p-6 space-y-6" style={{ fontFamily: 'Times New Roman, serif' }}>
              {/* 預覽內容 */}
              <div className="space-y-4">
                {/* 題幹預覽 */}
                <div>
                  <h4 
                    className="font-bold text-gray-900 mb-3"
                    style={{ fontSize: `${exportSettings.problem_font_size}px` }}
                  >
                    題目
                  </h4>
                  <div 
                    className="text-gray-800 leading-relaxed"
                    style={{ fontSize: `${exportSettings.problem_font_size}px` }}
                  >
                    <p>求解下列方程式：</p>
                    <div className="my-3">
                      <BlockMath math="\\frac{x^2 + 2x + 1}{x - 1} = 0" />
                    </div>
                  </div>
                </div>

                {/* 選項預覽 */}
                <div>
                  <h4 
                    className="font-bold text-gray-900 mb-3"
                    style={{ fontSize: `${exportSettings.problem_font_size}px` }}
                  >
                    選項
                  </h4>
                  <div 
                    className="text-gray-800 space-y-1"
                    style={{ fontSize: `${exportSettings.problem_font_size}px` }}
                  >
                    <p>(A) x = -1</p>
                    <p>(B) x = 1</p>
                    <p>(C) x = 0</p>
                    <p>(D) 無解</p>
                  </div>
                </div>

                {/* 詳解預覽 */}
                <div>
                  <h4 
                    className="font-bold text-gray-900 mb-3"
                    style={{ fontSize: `${exportSettings.solution_font_size}px` }}
                  >
                    解析
                  </h4>
                  <div 
                    className="text-gray-700 leading-relaxed space-y-2"
                    style={{ fontSize: `${exportSettings.solution_font_size}px` }}
                  >
                    <p>由於分母不能為零，所以 <InlineMath math="x \\neq 1" />。</p>
                    <p>分子 <InlineMath math="x^2 + 2x + 1 = (x + 1)^2 = 0" /></p>
                    <p>因此 <InlineMath math="x = -1" /></p>
                    <p>答案是 (A)。</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* OMML 驗證結果 */}
          {exportResult?.omml_validation && (
            <div className="bg-white rounded-lg shadow-sm p-6 mt-4">
              <h4 className="font-medium text-gray-900 mb-3">OMML 公式驗證</h4>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">總公式數量:</span>
                  <span className="font-medium">{exportResult.omml_validation.total_formulas}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">OMML 公式數量:</span>
                  <span className="font-medium">{exportResult.omml_validation.omml_formulas}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">轉換成功率:</span>
                  <span className={`font-medium ${
                    exportResult.omml_validation.omml_ratio === 1 ? 'text-success-600' : 'text-warning-600'
                  }`}>
                    {(exportResult.omml_validation.omml_ratio * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {exportResult.omml_validation.all_formulas_omml && (
                <div className="mt-3 p-3 bg-success-50 border border-success-200 rounded-lg">
                  <p className="text-sm text-success-700">
                    ✓ 所有公式已成功轉換為 OMML 格式，可在 Word 中直接編輯
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ExportPage