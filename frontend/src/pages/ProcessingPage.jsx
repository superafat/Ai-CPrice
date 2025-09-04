import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Loader, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

import { getTaskStatus, retryTask } from '../services/api'

const ProcessingPage = () => {
  const { taskId } = useParams()
  const navigate = useNavigate()
  const [taskStatus, setTaskStatus] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [retryingBlocks, setRetryingBlocks] = useState(new Set())

  useEffect(() => {
    if (taskId) {
      pollTaskStatus()
    }
  }, [taskId])

  const pollTaskStatus = async () => {
    try {
      const status = await getTaskStatus(taskId)
      setTaskStatus(status)
      setIsLoading(false)

      // 如果處理完成，導向預覽頁面
      if (status.stage === 'completed') {
        setTimeout(() => {
          navigate(`/preview/${taskId}`)
        }, 1500)
      } else if (status.stage === 'failed') {
        toast.error('處理失敗，請重試或聯繫客服')
      } else {
        // 繼續輪詢
        setTimeout(pollTaskStatus, 2000)
      }
    } catch (error) {
      console.error('獲取任務狀態失敗:', error)
      setIsLoading(false)
      toast.error('無法獲取處理狀態')
    }
  }

  const handleRetryBlock = async (blockId, useHighQuality = true) => {
    setRetryingBlocks(prev => new Set([...prev, blockId]))
    
    try {
      await retryTask(taskId, blockId, useHighQuality)
      toast.success('重試成功')
      
      // 重新獲取狀態
      await pollTaskStatus()
    } catch (error) {
      toast.error('重試失敗')
    } finally {
      setRetryingBlocks(prev => {
        const newSet = new Set(prev)
        newSet.delete(blockId)
        return newSet
      })
    }
  }

  const getStageDisplay = (stage) => {
    const stages = {
      'uploaded': { text: '檔案已上傳', icon: CheckCircle, color: 'text-success-500' },
      'preprocessing': { text: '影像前處理中', icon: Loader, color: 'text-blue-500' },
      'segmented': { text: '切塊分析中', icon: Loader, color: 'text-blue-500' },
      'classified': { text: '區塊分類中', icon: Loader, color: 'text-blue-500' },
      'ocr_processing': { text: 'OCR 識別中', icon: Loader, color: 'text-blue-500' },
      'standardizing': { text: '標準化處理中', icon: Loader, color: 'text-blue-500' },
      'completed': { text: '處理完成', icon: CheckCircle, color: 'text-success-500' },
      'failed': { text: '處理失敗', icon: AlertCircle, color: 'text-error-500' }
    }
    
    return stages[stage] || { text: '未知狀態', icon: AlertCircle, color: 'text-gray-500' }
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <Loader className="mx-auto h-12 w-12 text-blue-500 animate-spin" />
            <h2 className="mt-4 text-xl font-medium text-gray-900">載入中...</h2>
            <p className="mt-2 text-gray-600">正在獲取處理狀態</p>
          </div>
        </div>
      </div>
    )
  }

  if (!taskStatus) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-error-500" />
            <h2 className="mt-4 text-xl font-medium text-gray-900">找不到任務</h2>
            <p className="mt-2 text-gray-600">請檢查任務 ID 是否正確</p>
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

  const stageInfo = getStageDisplay(taskStatus.stage)
  const StageIcon = stageInfo.icon

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 處理狀態 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-medium text-gray-900">處理進度</h2>
          <span className="text-sm text-gray-500">任務 ID: {taskId}</span>
        </div>

        <div className="flex items-center space-x-4">
          <StageIcon className={`h-8 w-8 ${stageInfo.color} ${
            taskStatus.stage !== 'completed' && taskStatus.stage !== 'failed' ? 'animate-spin' : ''
          }`} />
          <div>
            <p className="text-lg font-medium text-gray-900">{stageInfo.text}</p>
            {taskStatus.message && (
              <p className="text-sm text-gray-600">{taskStatus.message}</p>
            )}
          </div>
        </div>

        {/* 進度條 */}
        {taskStatus.progress !== undefined && (
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>進度</span>
              <span>{taskStatus.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${taskStatus.progress}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* 區塊處理詳情 */}
      {taskStatus.blocks && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">區塊處理詳情</h3>
          
          <div className="space-y-3">
            {taskStatus.blocks.map((block, index) => (
              <div key={block.id || index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    block.status === 'completed' ? 'bg-success-500' :
                    block.status === 'failed' ? 'bg-error-500' :
                    'bg-blue-500 animate-pulse'
                  }`}></div>
                  
                  <div>
                    <p className="font-medium text-gray-900">
                      {block.type === 'problem' ? '題幹' :
                       block.type === 'options' ? '選項' :
                       block.type === 'formula' ? '公式' : '其他'}
                    </p>
                    {block.confidence && (
                      <p className="text-sm text-gray-600">
                        信心度: {(block.confidence * 100).toFixed(1)}%
                      </p>
                    )}
                  </div>
                </div>

                {/* 重試按鈕 */}
                {block.status === 'failed' && (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleRetryBlock(block.id, false)}
                      disabled={retryingBlocks.has(block.id)}
                      className="px-3 py-1 text-sm border border-gray-300 rounded text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                    >
                      {retryingBlocks.has(block.id) ? (
                        <Loader className="h-4 w-4 animate-spin" />
                      ) : (
                        '重試'
                      )}
                    </button>
                    
                    <button
                      onClick={() => handleRetryBlock(block.id, true)}
                      disabled={retryingBlocks.has(block.id)}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      高畫質重試
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 處理完成提示 */}
      {taskStatus.stage === 'completed' && (
        <div className="bg-success-50 border border-success-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <CheckCircle className="h-8 w-8 text-success-500" />
            <div>
              <h3 className="text-lg font-medium text-success-800">處理完成！</h3>
              <p className="text-success-700">已辨識完成，公式將以標準格式顯示</p>
              <p className="text-sm text-success-600 mt-1">正在跳轉到預覽頁面...</p>
            </div>
          </div>
        </div>
      )}

      {/* 處理失敗提示 */}
      {taskStatus.stage === 'failed' && (
        <div className="bg-error-50 border border-error-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <AlertCircle className="h-8 w-8 text-error-500" />
              <div>
                <h3 className="text-lg font-medium text-error-800">處理失敗</h3>
                <p className="text-error-700">{taskStatus.error || '未知錯誤'}</p>
              </div>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={() => navigate('/upload')}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                重新上傳
              </button>
              
              <button
                onClick={pollTaskStatus}
                className="px-4 py-2 bg-error-600 text-white rounded-lg hover:bg-error-700"
              >
                <RefreshCw className="h-4 w-4 mr-2 inline" />
                重試處理
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProcessingPage