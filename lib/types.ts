export interface DetectionResult {
  prediction: string;
  confidence: number;
  faces_detected: number;
  processing_time: string;
  face_coordinates?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  error?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
