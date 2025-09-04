import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, Image, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react'
import toast from 'react-hot-toast'

import ImageCropper from '../components/ImageCropper'
import PhotoGuide from '../components/PhotoGuide'
import { uploadFile } from '../services/api'

const UploadPage = () => {
  const navigate = useNavigate()
  const [uploadedFile, setUploadedFile] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [showCropper, setShowCropper] = useState(false)
  const [showGuide, setShowGuide] = useState(false)
  const [multipleProblemsDetected, setMultipleProblemsDetected] = useState(false)

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    // 檔案類型驗證
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
    if (!allowedTypes.includes(file.type)) {
      toast.error('不支援的檔案格式。請上傳 JPG、PNG、WebP 或 PDF 檔案。')
      return
    }

    // 檔案大小驗證
    const maxSize = 50 * 1024 * 1024 // 50MB
    if (file.size > maxSize) {
      toast.error('檔案大小超過 50MB 限制')
      return
    }

    setUploadedFile(file)
    
    // 簡單的多題檢測（基於檔案大小和類型）
    if (file.size > 5 * 1024 * 1024 || file.type === 'application/pdf') {
      setMultipleProblemsDetected(true)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    multiple: false
  })

  const handleUpload = async () => {
    if (!uploadedFile) {
      toast.error('請先選擇檔案')
      return
    }

    setIsProcessing(true)
    
    try {
      const formData = new FormData()
      formData.append('file', uploadedFile)
      formData.append('auto_process', 'true')

      const response = await uploadFile(formData)
      
      toast.success('檔案上傳成功，正在處理中...')
      
      // 導向處理頁面
      navigate(`/processing/${response.task_id}`)
      
    } catch (error) {
      console.error('上傳失敗:', error)
      toast.error('上傳失敗，請重試')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleCropComplete = (croppedFile) => {
    setUploadedFile(croppedFile)
    setShowCropper(false)
    setMultipleProblemsDetected(false)
    toast.success('裁切完成')
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* 頁面標題 */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">
          上傳題目圖片
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          支援物理/數學題目與詳解的圖檔或 PDF，自動識別並轉換為 Word 文檔
        </p>
      </div>

      {/* 上傳區域 */}
      <div className="bg-white rounded-lg shadow-sm border-2 border-dashed border-gray-300 p-8">
        <div
          {...getRootProps()}
          className={`text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-primary-500 bg-primary-50' : 'hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          
          <div className="space-y-4">
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            
            {isDragActive ? (
              <p className="text-lg text-primary-600">放開以上傳檔案...</p>
            ) : (
              <>
                <p className="text-lg text-gray-600">
                  拖拽檔案到此處，或點擊選擇檔案
                </p>
                <p className="text-sm text-gray-500">
                  支援 JPG、PNG、WebP、PDF 格式，最大 50MB
                </p>
              </>
            )}
          </div>
        </div>
      </div>

      {/* 已選擇的檔案 */}
      {uploadedFile && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">已選擇檔案</h3>
          
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              {uploadedFile.type.startsWith('image/') ? (
                <Image className="h-8 w-8 text-blue-500" />
              ) : (
                <FileText className="h-8 w-8 text-red-500" />
              )}
              <div>
                <p className="font-medium text-gray-900">{uploadedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(uploadedFile.size / 1024 / 1024).toFixed(1)} MB
                </p>
              </div>
            </div>
            
            <button
              onClick={() => setUploadedFile(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          {/* 多題檢測警告 */}
          {multipleProblemsDetected && (
            <div className="mt-4 p-4 bg-warning-50 border border-warning-200 rounded-lg">
              <div className="flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-warning-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-warning-800">
                    偵測到多個題目
                  </h4>
                  <p className="text-sm text-warning-700 mt-1">
                    建議裁成單題可提升準確率與速度
                  </p>
                  <button
                    onClick={() => setShowCropper(true)}
                    className="mt-2 text-sm text-warning-800 underline hover:text-warning-900"
                  >
                    使用裁切工具
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 操作按鈕 */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={() => setShowGuide(true)}
          className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          查看拍攝建議
        </button>
        
        <button
          onClick={handleUpload}
          disabled={!uploadedFile || isProcessing}
          className={`px-8 py-3 rounded-lg font-medium transition-colors ${
            !uploadedFile || isProcessing
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-primary-600 text-white hover:bg-primary-700'
          }`}
        >
          {isProcessing ? (
            <div className="flex items-center space-x-2">
              <Loader className="h-4 w-4 animate-spin" />
              <span>處理中...</span>
            </div>
          ) : (
            '開始處理'
          )}
        </button>
      </div>

      {/* 功能說明 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">系統功能</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-success-500" />
              <span className="text-gray-700">自動影像前處理與切塊</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-success-500" />
              <span className="text-gray-700">雙引擎 OCR 識別</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-success-500" />
              <span className="text-gray-700">LaTeX 公式標準化</span>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-success-500" />
              <span className="text-gray-700">Word 原生公式 (OMML)</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-success-500" />
              <span className="text-gray-700">自訂字體大小</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-success-500" />
              <span className="text-gray-700">圖片原位插入</span>
            </div>
          </div>
        </div>
      </div>

      {/* 裁切工具彈窗 */}
      {showCropper && uploadedFile && (
        <ImageCropper
          file={uploadedFile}
          onComplete={handleCropComplete}
          onCancel={() => setShowCropper(false)}
        />
      )}

      {/* 拍攝指南彈窗 */}
      {showGuide && (
        <PhotoGuide onClose={() => setShowGuide(false)} />
      )}
    </div>
  )
}

export default Layout