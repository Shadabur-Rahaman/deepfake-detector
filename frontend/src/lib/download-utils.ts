/**
 * Enhanced download utilities for reliable file downloads across all browsers
 */

export interface DownloadOptions {
  filename: string
  mimeType?: string
  fallbackText?: string
}

/**
 * Downloads a blob as a file with enhanced browser compatibility
 */
export const downloadBlob = async (
  blob: Blob, 
  options: DownloadOptions
): Promise<boolean> => {
  const { filename, mimeType, fallbackText } = options

  try {
    // Method 1: Modern browsers with download attribute support
    if (typeof window !== 'undefined' && 'URL' in window && 'createObjectURL' in window) {
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      
      // Set all necessary attributes
      link.href = url
      link.download = filename
      link.style.display = 'none'
      link.setAttribute('target', '_blank')
      link.setAttribute('rel', 'noopener noreferrer')
      
      // Add to DOM
      document.body.appendChild(link)
      
      // Trigger download with proper timing
      return new Promise((resolve) => {
        // Use requestAnimationFrame to ensure DOM is ready
        requestAnimationFrame(() => {
          try {
            link.click()
            
            // Clean up after download starts
            setTimeout(() => {
              if (document.body.contains(link)) {
                document.body.removeChild(link)
              }
              URL.revokeObjectURL(url)
              resolve(true)
            }, 100)
          } catch (error) {
            console.warn('Primary download method failed:', error)
            resolve(false)
          }
        })
      })
    }
    
    return false
  } catch (error) {
    console.error('Download failed:', error)
    return false
  }
}

/**
 * Fallback download method using data URL
 */
export const downloadDataURL = (dataUrl: string, filename: string): boolean => {
  try {
    const link = document.createElement('a')
    link.href = dataUrl
    link.download = filename
    link.style.display = 'none'
    link.setAttribute('target', '_blank')
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    return true
  } catch (error) {
    console.error('Data URL download failed:', error)
    return false
  }
}

/**
 * Convert blob to data URL for fallback download
 */
export const blobToDataURL = (blob: Blob): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

/**
 * Enhanced download with multiple fallback methods
 */
export const downloadFile = async (
  blob: Blob, 
  options: DownloadOptions
): Promise<boolean> => {
  const { filename, mimeType, fallbackText } = options

  // Method 1: Standard blob download
  const success = await downloadBlob(blob, options)
  if (success) return true

  // Method 2: Data URL fallback
  try {
    const dataUrl = await blobToDataURL(blob)
    return downloadDataURL(dataUrl, filename)
  } catch (error) {
    console.warn('Data URL fallback failed:', error)
  }

  // Method 3: Open in new tab as last resort
  try {
    const url = URL.createObjectURL(blob)
    const newWindow = window.open(url, '_blank')
    if (newWindow) {
      // Clean up URL after a delay
      setTimeout(() => URL.revokeObjectURL(url), 1000)
      return true
    }
  } catch (error) {
    console.warn('New tab fallback failed:', error)
  }

  // Method 4: Show user instructions
  if (fallbackText) {
    alert(fallbackText)
  }

  return false
}

/**
 * Check if browser supports programmatic downloads
 */
export const supportsDownload = (): boolean => {
  return typeof window !== 'undefined' && 
         'URL' in window && 
         'createObjectURL' in window &&
         typeof document.createElement('a').download !== 'undefined'
}

/**
 * Get browser-specific download instructions
 */
export const getDownloadInstructions = (filename: string): string => {
  const userAgent = navigator.userAgent.toLowerCase()
  
  if (userAgent.includes('chrome')) {
    return `Your download should start automatically. If not, check your browser's download settings or try right-clicking and "Save link as..." on the download button.`
  } else if (userAgent.includes('firefox')) {
    return `Your download should start automatically. If not, check your browser's download settings or try right-clicking and "Save link as..." on the download button.`
  } else if (userAgent.includes('safari')) {
    return `Your download should start automatically. If not, try right-clicking and "Save link as..." on the download button.`
  } else if (userAgent.includes('edge')) {
    return `Your download should start automatically. If not, check your browser's download settings or try right-clicking and "Save link as..." on the download button.`
  } else {
    return `Your download should start automatically. If not, try right-clicking and "Save link as..." on the download button.`
  }
}
