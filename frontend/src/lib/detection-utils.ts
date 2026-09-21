// Detection result utilities for consistent formatting and color coding

export interface DetectionResultData {
  final_result?: string;
  prediction?: string;
  authentic?: boolean;
  confidence: number;
  faces_analyzed?: number;
  faces_detected?: number;
  processing_time?: number;
  bias_applied?: number;
  metadata_flags?: string[];
}

export interface FormattedDetectionResult {
  label: string;
  color: string;
  bgColor: string;
  borderColor: string;
  confidence: number;
  confidenceText: string;
  isAuthentic: boolean;
}

/**
 * Formats detection result with proper color coding and labels
 */
export function formatDetectionResult(data: DetectionResultData): FormattedDetectionResult {
  // Get the actual result text
  const resultText = data.final_result || data.prediction || 'Unknown';
  
  // Determine if the result is authentic/real
  const isAuthentic = resultText.toLowerCase().includes('real') || 
                     resultText.toLowerCase().includes('authentic') ||
                     resultText === 'Real Face' ||
                     data.authentic === true;

  // Format confidence to 2 decimal places
  const confidence = typeof data.confidence === 'number' ? data.confidence : 0;
  const confidenceText = confidence.toFixed(2);

  // Set colors and label based on result
  let colors;
  if (isAuthentic) {
    colors = {
      color: '#28A745', // Green for authentic
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      borderColor: 'border-green-200 dark:border-green-800',
      label: 'Authentic / Real'
    };
  } else if (resultText.toLowerCase().includes('deepfake') || 
             resultText.toLowerCase().includes('fake') ||
             resultText.toLowerCase().includes('synthetic')) {
    colors = {
      color: '#FF4C4C', // Red for deepfake
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      borderColor: 'border-red-200 dark:border-red-800',
      label: 'Deepfake Detected'
    };
  } else {
    // Handle other results like "Poor Face Quality", "No Faces Detected", etc.
    colors = {
      color: '#FFA500', // Orange for other results
      bgColor: 'bg-orange-50 dark:bg-orange-900/20',
      borderColor: 'border-orange-200 dark:border-orange-800',
      label: resultText // Use the actual result text
    };
  }

  return {
    label: colors.label,
    color: colors.color,
    bgColor: colors.bgColor,
    borderColor: colors.borderColor,
    confidence,
    confidenceText,
    isAuthentic
  };
}

/**
 * Gets confidence color class for styling
 */
export function getConfidenceColorClass(confidence: number): string {
  if (confidence >= 90) return 'text-green-600 dark:text-green-400';
  if (confidence >= 70) return 'text-yellow-600 dark:text-yellow-400';
  if (confidence >= 50) return 'text-orange-600 dark:text-orange-400';
  return 'text-red-600 dark:text-red-400';
}

/**
 * Formats confidence percentage with proper styling
 */
export function formatConfidenceDisplay(confidence: number | undefined): string {
  if (confidence === undefined || confidence === null || isNaN(confidence)) {
    return '0.0%';
  }
  
  // If confidence is already a percentage (>= 1), use it as is
  // If confidence is a decimal (0-1), convert to percentage
  const percentage = confidence >= 1 ? confidence : confidence * 100;
  return `${percentage.toFixed(1)}%`;
}

/**
 * Formats confidence for display without percentage symbol (for use with existing % symbols)
 */
export function formatConfidenceValue(confidence: number | undefined): string {
  if (confidence === undefined || confidence === null || isNaN(confidence)) {
    return '0.0';
  }
  
  // If confidence is already a percentage (>= 1), use it as is
  // If confidence is a decimal (0-1), convert to percentage
  const percentage = confidence >= 1 ? confidence : confidence * 100;
  return percentage.toFixed(1);
}

/**
 * Creates a tooltip text for bias applied information
 */
export function getBiasTooltipText(biasApplied: number): string {
  if (biasApplied === 0) return 'No bias applied from metadata analysis';
  return `Bias applied: ${(biasApplied * 100).toFixed(1)}% from title/metadata detection`;
}
