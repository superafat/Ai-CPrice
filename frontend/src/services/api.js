/**
 * API 服務模組
 */
import axios from 'axios'

// 建立 axios 實例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    // 可以在這裡添加認證 token
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 回應攔截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '請求失敗'
    return Promise.reject(new Error(message))
  }
)

// 檔案上傳 API
export const uploadFile = async (formData) => {
  const response = await axios.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000,
  })
  return response.data
}

// 獲取任務狀態
export const getTaskStatus = async (taskId) => {
  return await api.get(`/upload/status/${taskId}`)
}

// 重試處理
export const retryTask = async (taskId, blockId, useHighQuality = true) => {
  return await api.post('/ocr/retry', {
    task_id: taskId,
    block_id: blockId,
    use_high_quality: useHighQuality
  })
}

// 獲取預覽內容
export const getPreviewContent = async (taskId) => {
  return await api.get(`/export/preview/${taskId}`)
}

// 更新區塊內容
export const updateBlockContent = async (taskId, blockId, content) => {
  return await api.post('/ocr/update-block', {
    task_id: taskId,
    block_id: blockId,
    content: content
  })
}

// 獲取匯出設定
export const getExportSettings = async () => {
  return await api.get('/export/settings/default')
}

// 匯出 Word 文檔
export const exportToWord = async (taskId, exportSettings) => {
  return await api.post('/export/word', {
    task_id: taskId,
    export_settings: exportSettings
  })
}

// 批次匯出
export const batchExport = async (taskIds, exportSettings) => {
  return await api.post('/export/batch', {
    task_ids: taskIds,
    export_settings: exportSettings
  })
}

// 驗證 LaTeX
export const validateLatex = async (latexText) => {
  return await api.post('/validate/latex', {
    latex_text: latexText
  })
}

// 管理 API
export const getSystemStats = async () => {
  return await api.get('/management/stats')
}

export const getDashboardData = async () => {
  return await api.get('/management/dashboard')
}

export const getErrorList = async (params = {}) => {
  return await api.get('/management/errors', { params })
}

export const submitErrorReport = async (errorReport) => {
  return await api.post('/management/error-report', errorReport)
}

export const resetDailyQuota = async () => {
  return await api.post('/management/quota/reset')
}

export const getQuotaStatus = async () => {
  return await api.get('/management/quota/status')
}

export const cleanupOldFiles = async (daysOld = 7) => {
  return await api.post('/management/cleanup', { days_old: daysOld })
}