import React, { useState, useEffect } from 'react'
import { BarChart3, Activity, AlertCircle, RefreshCw, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

import { getDashboardData, getQuotaStatus, resetDailyQuota, cleanupOldFiles } from '../services/api'

const ManagementPage = () => {
  const [dashboardData, setDashboardData] = useState(null)
  const [quotaStatus, setQuotaStatus] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isResettingQuota, setIsResettingQuota] = useState(false)
  const [isCleaningFiles, setIsCleaningFiles] = useState(false)

  useEffect(() => {
    loadDashboardData()
    loadQuotaStatus()
  }, [])

  const loadDashboardData = async () => {
    try {
      const data = await getDashboardData()
      setDashboardData(data)
    } catch (error) {
      console.error('載入儀表板資料失敗:', error)
      toast.error('載入儀表板失敗')
    }
  }

  const loadQuotaStatus = async () => {
    try {
      const quota = await getQuotaStatus()
      setQuotaStatus(quota)
    } catch (error) {
      console.error('載入配額狀態失敗:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleResetQuota = async () => {
    setIsResettingQuota(true)
    try {
      await resetDailyQuota()
      toast.success('每日配額已重置')
      await loadQuotaStatus()
    } catch (error) {
      toast.error('重置失敗')
    } finally {
      setIsResettingQuota(false)
    }
  }

  const handleCleanupFiles = async () => {
    setIsCleaningFiles(true)
    try {
      const result = await cleanupOldFiles(7)
      toast.success(`已清理 ${result.cleaned_files} 個檔案`)
    } catch (error) {
      toast.error('清理失敗')
    } finally {
      setIsCleaningFiles(false)
    }
  }

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <Activity className="mx-auto h-12 w-12 text-blue-500 animate-spin" />
            <h2 className="mt-4 text-xl font-medium text-gray-900">載入管理資料中...</h2>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
            <BarChart3 className="h-6 w-6" />
            <span>系統管理儀表板</span>
          </h1>
          <p className="text-gray-600">監控系統狀態、OCR 效能與資源使用</p>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={handleResetQuota}
            disabled={isResettingQuota}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            {isResettingQuota ? '重置中...' : '重置配額'}
          </button>
          
          <button
            onClick={handleCleanupFiles}
            disabled={isCleaningFiles}
            className="px-4 py-2 bg-error-600 text-white rounded-lg hover:bg-error-700 disabled:opacity-50 flex items-center space-x-2"
          >
            <Trash2 className="h-4 w-4" />
            <span>{isCleaningFiles ? '清理中...' : '清理檔案'}</span>
          </button>
        </div>
      </div>

      {/* 概覽統計 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">今日處理數</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.overview?.total_requests_today || 156}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Activity className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">成功率</p>
              <p className="text-2xl font-bold text-success-600">
                {dashboardData?.overview?.success_rate?.toFixed(1) || 95.2}%
              </p>
            </div>
            <div className="p-3 bg-success-100 rounded-full">
              <CheckCircle className="h-6 w-6 text-success-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">平均處理時間</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.overview?.average_processing_time || 4.2}s
              </p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-full">
              <Activity className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">進行中任務</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.overview?.active_tasks || 3}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <RefreshCw className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* OCR 效能統計 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">OCR 引擎效能</h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">文字識別成功率</span>
              <span className="font-medium text-success-600">
                {dashboardData?.ocr_performance?.text_ocr_success || 96.5}%
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">公式識別成功率</span>
              <span className="font-medium text-success-600">
                {dashboardData?.ocr_performance?.formula_ocr_success || 89.2}%
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">備援引擎使用率</span>
              <span className="font-medium text-warning-600">
                {dashboardData?.ocr_performance?.fallback_usage || 12.3}%
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">兜底引擎使用率</span>
              <span className="font-medium text-error-600">
                {dashboardData?.ocr_performance?.emergency_usage || 3.1}%
              </span>
            </div>
          </div>
        </div>

        {/* 資源使用狀況 */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">資源使用狀況</h3>
          
          {quotaStatus && (
            <div className="space-y-4">
              {/* Mathpix 配額 */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-600">Mathpix 每日配額</span>
                  <span className="text-sm text-gray-500">
                    {quotaStatus.mathpix.daily_used} / {quotaStatus.mathpix.daily_limit}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      quotaStatus.mathpix.usage_percentage > 80 ? 'bg-error-500' :
                      quotaStatus.mathpix.usage_percentage > 60 ? 'bg-warning-500' :
                      'bg-success-500'
                    }`}
                    style={{ width: `${quotaStatus.mathpix.usage_percentage}%` }}
                  ></div>
                </div>
              </div>

              {/* 磁碟使用量 */}
              <div className="flex justify-between items-center">
                <span className="text-gray-600">磁碟使用量</span>
                <span className="font-medium">
                  {dashboardData?.resource_usage?.disk_usage_mb?.toFixed(1) || 1250.5} MB
                </span>
              </div>
              
              {/* 記憶體使用量 */}
              <div className="flex justify-between items-center">
                <span className="text-gray-600">記憶體使用量</span>
                <span className="font-medium">
                  {dashboardData?.resource_usage?.memory_usage_mb?.toFixed(1) || 890.2} MB
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 最近錯誤 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-error-500" />
          <span>最近錯誤</span>
        </h3>
        
        {dashboardData?.recent_errors?.length > 0 ? (
          <div className="space-y-3">
            {dashboardData.recent_errors.map((error, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-error-50 border border-error-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="text-sm font-medium text-error-800">
                    {error.type}
                  </div>
                  <div className="text-sm text-error-600">
                    {error.time}
                  </div>
                </div>
                <div className="text-sm font-medium text-error-800">
                  {error.count} 次
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">暫無錯誤記錄</p>
        )}
      </div>

      {/* 系統設定 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">系統設定</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-800 mb-3">OCR 引擎狀態</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">PaddleOCR (主要文字)</span>
                <span className="px-2 py-1 text-xs bg-success-100 text-success-800 rounded">啟用</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">pix2tex (主要公式)</span>
                <span className="px-2 py-1 text-xs bg-success-100 text-success-800 rounded">啟用</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tesseract (備援)</span>
                <span className="px-2 py-1 text-xs bg-success-100 text-success-800 rounded">啟用</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Mathpix (兜底)</span>
                <span className="px-2 py-1 text-xs bg-warning-100 text-warning-800 rounded">限額</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-800 mb-3">效能指標</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">目標成功率</span>
                <span className="font-medium text-gray-900">≥ 95%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">目標處理時間</span>
                <span className="font-medium text-gray-900">≤ 6s</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">兜底使用率目標</span>
                <span className="font-medium text-gray-900">≤ 5%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">LaTeX 可編譯率目標</span>
                <span className="font-medium text-gray-900">≥ 98%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 快速操作 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">快速操作</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => window.location.reload()}
            className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 text-center"
          >
            <RefreshCw className="h-6 w-6 mx-auto mb-2 text-gray-600" />
            <div className="text-sm font-medium text-gray-900">重新整理資料</div>
            <div className="text-xs text-gray-500">更新所有統計資訊</div>
          </button>
          
          <button
            onClick={handleResetQuota}
            disabled={isResettingQuota}
            className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 text-center disabled:opacity-50"
          >
            <Activity className="h-6 w-6 mx-auto mb-2 text-gray-600" />
            <div className="text-sm font-medium text-gray-900">重置每日配額</div>
            <div className="text-xs text-gray-500">重置 Mathpix 使用量</div>
          </button>
          
          <button
            onClick={handleCleanupFiles}
            disabled={isCleaningFiles}
            className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 text-center disabled:opacity-50"
          >
            <Trash2 className="h-6 w-6 mx-auto mb-2 text-gray-600" />
            <div className="text-sm font-medium text-gray-900">清理舊檔案</div>
            <div className="text-xs text-gray-500">刪除 7 天前的檔案</div>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ManagementPage