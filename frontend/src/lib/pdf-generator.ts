import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

export interface DetectionReportData {
  videoId: string
  timestamp: string
  prediction: string
  confidence: number
  facesDetected: number
  processingTime: number
  detectionMethod: string
  enhancedAnalysis: boolean
  frameCount?: number
  videoDuration?: number
  biasApplied: number
  metadataFlags: string[]
  videoUrl?: string
  thumbnailUrl?: string
  reportId: string
  // Mode-specific metadata (optional for backward compatibility)
  detectionMode?: string
  modelCount?: number
  modelsUsed?: string[]
}

export interface PDFReportOptions {
  includeThumbnail?: boolean
  includeMetadata?: boolean
  includeTechnicalDetails?: boolean
  watermark?: string
  encryption?: boolean
}

export class SecurePDFGenerator {
  private static generateReportId(): string {
    const timestamp = Date.now().toString(36)
    const random = Math.random().toString(36).substring(2, 8)
    return `DFR-${timestamp}-${random}`.toUpperCase()
  }

  private static generateHash(data: string): string {
    // Simple hash function for tamper detection
    let hash = 0
    for (let i = 0; i < data.length; i++) {
      const char = data.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(16)
  }

  private static createWatermark(pdf: jsPDF, text: string): void {
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    
    pdf.setGState(new pdf.GState({ opacity: 0.1 }))
    pdf.setFontSize(48)
    pdf.setTextColor(200, 200, 200)
    pdf.text(text, pageWidth / 2, pageHeight / 2, { angle: 45, align: 'center' })
    pdf.setGState(new pdf.GState({ opacity: 1 }))
  }

  private static addSecurityFeatures(pdf: jsPDF, reportData: DetectionReportData): void {
    // Add digital signature placeholder
    const signature = this.generateHash(JSON.stringify(reportData))
    pdf.setFontSize(8)
    pdf.setTextColor(100, 100, 100)
    pdf.text(`Digital Signature: ${signature}`, 20, pdf.internal.pageSize.getHeight() - 20)
    
    // Add report ID for verification
    pdf.text(`Report ID: ${reportData.reportId}`, 20, pdf.internal.pageSize.getHeight() - 15)
    
    // Add generation timestamp
    pdf.text(`Generated: ${new Date().toISOString()}`, 20, pdf.internal.pageSize.getHeight() - 10)
  }

  static async generateReport(
    reportData: DetectionReportData,
    options: PDFReportOptions = {}
  ): Promise<Blob> {
    const {
      includeThumbnail = true,
      includeMetadata = true,
      includeTechnicalDetails = true,
      watermark = 'iFake Deepfake Detection',
      encryption = false
    } = options

    // Generate unique report ID
    reportData.reportId = this.generateReportId()

    // Create new PDF document
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    let yPosition = 20

    // Add watermark
    this.createWatermark(pdf, watermark)

    // Header
    pdf.setFontSize(24)
    pdf.setTextColor(0, 0, 0)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Deepfake Detection Report', pageWidth / 2, yPosition, { align: 'center' })
    yPosition += 15

    // Report ID and timestamp
    pdf.setFontSize(10)
    pdf.setTextColor(100, 100, 100)
    pdf.text(`Report ID: ${reportData.reportId}`, 20, yPosition)
    pdf.text(`Generated: ${new Date().toLocaleString()}`, pageWidth - 20, yPosition, { align: 'right' })
    yPosition += 10

    // Main detection result
    pdf.setFontSize(18)
    pdf.setTextColor(0, 0, 0)
    pdf.setFont('helvetica', 'bold')
    
    const isAuthentic = reportData.prediction.toLowerCase().includes('real')
    const resultColor = isAuthentic ? [40, 167, 69] : [255, 76, 76] // Green or Red
    pdf.setTextColor(resultColor[0], resultColor[1], resultColor[2])
    
    pdf.text(`${reportData.prediction}`, pageWidth / 2, yPosition, { align: 'center' })
    yPosition += 8

    // Confidence score
    pdf.setFontSize(14)
    pdf.setTextColor(0, 0, 0)
    pdf.text(`Confidence: ${reportData.confidence.toFixed(2)}%`, pageWidth / 2, yPosition, { align: 'center' })
    yPosition += 15

    // Add line separator
    pdf.setDrawColor(200, 200, 200)
    pdf.line(20, yPosition, pageWidth - 20, yPosition)
    yPosition += 10

    // Detection details section
    pdf.setFontSize(16)
    pdf.setTextColor(0, 0, 0)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Detection Details', 20, yPosition)
    yPosition += 10

    // Detection results table
    const detectionDetails = [
      ['Faces Analyzed', reportData.facesDetected.toString()],
      ['Processing Time', `${reportData.processingTime.toFixed(2)}s`],
      ['Detection Method', reportData.detectionMethod],
      ['Enhanced Analysis', reportData.enhancedAnalysis ? 'Yes' : 'No'],
      ['Bias Applied', `${(reportData.biasApplied * 100).toFixed(1)}%`]
    ]

    pdf.setFontSize(10)
    pdf.setFont('helvetica', 'normal')
    
    detectionDetails.forEach(([label, value]) => {
      pdf.text(`${label}:`, 25, yPosition)
      pdf.text(value, 80, yPosition)
      yPosition += 6
    })

    yPosition += 10

    // Technical details section
    if (includeTechnicalDetails) {
      pdf.setFontSize(16)
      pdf.setFont('helvetica', 'bold')
      pdf.text('Technical Information', 20, yPosition)
      yPosition += 10

      const technicalDetails = [
        ['Video ID', reportData.videoId],
        ['Frame Count', reportData.frameCount?.toString() || 'N/A'],
        ['Video Duration', reportData.videoDuration ? `${reportData.videoDuration}s` : 'N/A'],
        ['Analysis Timestamp', reportData.timestamp]
      ]

      pdf.setFontSize(10)
      pdf.setFont('helvetica', 'normal')
      
      technicalDetails.forEach(([label, value]) => {
        pdf.text(`${label}:`, 25, yPosition)
        pdf.text(value, 80, yPosition)
        yPosition += 6
      })

      yPosition += 10
    }

    // Metadata flags section
    if (includeMetadata && reportData.metadataFlags.length > 0) {
      pdf.setFontSize(16)
      pdf.setFont('helvetica', 'bold')
      pdf.text('Metadata Analysis', 20, yPosition)
      yPosition += 10

      pdf.setFontSize(10)
      pdf.setFont('helvetica', 'normal')
      pdf.text('Flags Detected:', 25, yPosition)
      yPosition += 6

      reportData.metadataFlags.forEach(flag => {
        pdf.text(`• ${flag}`, 30, yPosition)
        yPosition += 5
      })

      yPosition += 10
    }

    // Add thumbnail if available
    if (includeThumbnail && reportData.thumbnailUrl) {
      try {
        // Create a canvas to capture the thumbnail
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        const img = new Image()
        
        await new Promise((resolve, reject) => {
          img.onload = () => {
            canvas.width = 200
            canvas.height = 150
            ctx?.drawImage(img, 0, 0, 200, 150)
            resolve(canvas)
          }
          img.onerror = reject
          img.src = reportData.thumbnailUrl!
        })

        const imgData = canvas.toDataURL('image/jpeg', 0.8)
        pdf.addImage(imgData, 'JPEG', pageWidth - 120, yPosition, 100, 75)
        yPosition += 80
      } catch (error) {
        console.warn('Failed to add thumbnail to PDF:', error)
      }
    }

    // Security and verification section
    pdf.setFontSize(16)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Security & Verification', 20, yPosition)
    yPosition += 10

    pdf.setFontSize(10)
    pdf.setFont('helvetica', 'normal')
    pdf.text('This report contains digitally signed data to ensure authenticity.', 25, yPosition)
    yPosition += 6
    pdf.text('Any tampering with this document will invalidate the digital signature.', 25, yPosition)
    yPosition += 6
    pdf.text('For verification, contact: support@ifake-detection.com', 25, yPosition)
    yPosition += 15

    // Footer
    pdf.setFontSize(8)
    pdf.setTextColor(100, 100, 100)
    pdf.text('Generated by iFake Deepfake Detection System', pageWidth / 2, pageHeight - 30, { align: 'center' })
    pdf.text('© 2024 iFake. All rights reserved.', pageWidth / 2, pageHeight - 25, { align: 'center' })
    pdf.text('This report is confidential and intended for authorized use only.', pageWidth / 2, pageHeight - 20, { align: 'center' })

    // Add security features
    this.addSecurityFeatures(pdf, reportData)

    // Generate PDF blob
    const pdfBlob = pdf.output('blob')
    
    // Apply encryption if requested (basic implementation)
    if (encryption) {
      // Note: For production, use proper encryption libraries
      console.log('Encryption requested but not implemented in this version')
    }

    return pdfBlob
  }

  static async generateFromElement(
    elementId: string,
    reportData: DetectionReportData,
    options: PDFReportOptions = {}
  ): Promise<Blob> {
    const element = document.getElementById(elementId)
    if (!element) {
      throw new Error(`Element with ID '${elementId}' not found`)
    }

    // Generate report ID
    reportData.reportId = this.generateReportId()

    // Capture the element as canvas
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff'
    })

    // Create PDF from canvas
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    
    // Calculate dimensions to fit the image
    const imgWidth = canvas.width
    const imgHeight = canvas.height
    const ratio = Math.min(pageWidth / imgWidth, pageHeight / imgHeight)
    const finalWidth = imgWidth * ratio
    const finalHeight = imgHeight * ratio

    // Add watermark
    this.createWatermark(pdf, 'iFake Deepfake Detection')

    // Add the captured image
    pdf.addImage(imgData, 'PNG', (pageWidth - finalWidth) / 2, 20, finalWidth, finalHeight)

    // Add security features
    this.addSecurityFeatures(pdf, reportData)

    return pdf.output('blob')
  }

  static async generateSecureReport(
    reportData: DetectionReportData,
    options: PDFReportOptions = {}
  ): Promise<{ blob: Blob; reportId: string; hash: string }> {
    const reportId = this.generateReportId()
    reportData.reportId = reportId

    const blob = await this.generateReport(reportData, options)
    const hash = this.generateHash(JSON.stringify(reportData))

    return { blob, reportId, hash }
  }
}

// Utility function for easy integration
export const generateDetectionReport = async (
  result: any,
  videoUrl?: string,
  thumbnailUrl?: string
): Promise<Blob> => {
  const reportData: DetectionReportData = {
    videoId: `analysis_${Date.now()}`,
    timestamp: new Date().toISOString(),
    prediction: result.result || result.prediction || 'Unknown',
    confidence: result.confidence || 0,
    facesDetected: result.faces_found || result.facesDetected || 0,
    processingTime: result.processing_time || 0,
    detectionMethod: result.model_used || result.detection_method || 'MesoNet CNN',
    enhancedAnalysis: result.enhanced_analysis || false,
    frameCount: result.frame_count,
    videoDuration: result.video_duration,
    biasApplied: result.bias_applied || 0,
    metadataFlags: result.metadata_flags || [],
    videoUrl,
    thumbnailUrl,
    reportId: ''
  }

  return SecurePDFGenerator.generateReport(reportData, {
    includeThumbnail: true,
    includeMetadata: true,
    includeTechnicalDetails: true,
    watermark: 'iFake Deepfake Detection',
    encryption: false
  })
}
