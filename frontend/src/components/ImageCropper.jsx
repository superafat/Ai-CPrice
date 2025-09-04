import React, { useState, useCallback } from 'react'
import ReactCrop from 'react-image-crop'
import 'react-image-crop/dist/ReactCrop.css'
import { Crop, Check, X } from 'lucide-react'

const ImageCropper = ({ file, onComplete, onCancel }) => {
  const [imageSrc, setImageSrc] = useState(null)
  const [crop, setCrop] = useState({
    unit: '%',
    width: 80,
    height: 60,
    x: 10,
    y: 20
  })
  const [completedCrop, setCompletedCrop] = useState(null)
  const [imageRef, setImageRef] = useState(null)

  React.useEffect(() => {
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => setImageSrc(e.target.result)
      reader.readAsDataURL(file)
    }
  }, [file])

  const onImageLoad = useCallback((img) => {
    setImageRef(img)
  }, [])

  const handleCropComplete = async () => {
    if (!imageRef || !completedCrop) {
      return
    }

    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    const scaleX = imageRef.naturalWidth / imageRef.width
    const scaleY = imageRef.naturalHeight / imageRef.height
    
    canvas.width = completedCrop.width * scaleX
    canvas.height = completedCrop.height * scaleY
    
    ctx.drawImage(
      imageRef,
      completedCrop.x * scaleX,
      completedCrop.y * scaleY,
      completedCrop.width * scaleX,
      completedCrop.height * scaleY,
      0,
      0,
      completedCrop.width * scaleX,
      completedCrop.height * scaleY
    )

    canvas.toBlob(
      (blob) => {
        const croppedFile = new File([blob], file.name, { type: file.type })
        onComplete(croppedFile)
      },
      file.type,
      0.95
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-100 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 flex items-center space-x-2">
            <Crop className="h-5 w-5" />
            <span>裁切工具</span>
          </h3>
          
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6 overflow-auto max-h-[calc(90vh-120px)]">
          {imageSrc && (
            <div className="text-center">
              <ReactCrop
                crop={crop}
                onChange={(newCrop) => setCrop(newCrop)}
                onComplete={(newCrop) => setCompletedCrop(newCrop)}
                aspect={undefined}
                minWidth={200}
                minHeight={150}
              >
                <img
                  ref={setImageRef}
                  src={imageSrc}
                  onLoad={onImageLoad}
                  alt="待裁切圖片"
                  className="max-w-full h-auto"
                />
              </ReactCrop>
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
          <div className="text-sm text-gray-600">
            <p>拖拽選擇要保留的區域，建議包含完整的單一題目</p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              取消
            </button>
            
            <button
              onClick={handleCropComplete}
              disabled={!completedCrop}
              className={`px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
                !completedCrop
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-primary-600 text-white hover:bg-primary-700'
              }`}
            >
              <Check className="h-4 w-4" />
              <span>完成裁切</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ImageCropper