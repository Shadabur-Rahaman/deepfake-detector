"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, Shield, Code, Terminal, Copy, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';

export default function ApiDocs() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const copyToClipboard = async (code: string, id: string) => {
    await navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Navigation */}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Badge className="mb-4 bg-blue-100 text-blue-800">
            <Code className="w-3 h-3 mr-1" />
            REST API
          </Badge>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            iFake API Documentation
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Integrate deepfake detection into your applications with our simple REST API
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <motion.div
            className="lg:col-span-1"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle className="text-lg">Quick Navigation</CardTitle>
              </CardHeader>
              <CardContent>
                  {[
                    { href: "#getting-started", label: "Getting Started" },
                    { href: "#authentication", label: "Authentication" },
                    { href: "#endpoints", label: "API Endpoints" },
                    { href: "#examples", label: "Code Examples" },
                    { href: "#response-format", label: "Response Format" },
                    { href: "#rate-limits", label: "Rate Limits" }
                  ].map((item) => (
                    <a
                      key={item.href}
                      href={item.href}
                      className="block px-3 py-2 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                    >
                      {item.label}
                    </a>
                  ))}

              </CardContent>
            </Card>
          </motion.div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-8">
            {/* Getting Started */}
            <motion.section
              id="getting-started"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Getting Started</CardTitle>
                  <CardDescription>
                    Learn how to integrate iFake API into your application
                  </CardDescription>
                </CardHeader>
                <CardContent className="prose prose-sm max-w-none">
                  <p className="text-gray-600 leading-relaxed">
                    The iFake API provides a simple REST interface for deepfake detection. 
                    All requests are made to <code className="bg-gray-100 px-1 py-0.5 rounded">https://api.ifake.ai/v1/</code> 
                    and return JSON responses.
                  </p>
                  
                  <div className="mt-6">
                    <h4 className="font-semibold text-gray-900 mb-3">Base URL</h4>
                    <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm">
                      https://api.ifake.ai/v1/
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.section>

            {/* Authentication */}
            <motion.section
              id="authentication"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Authentication</CardTitle>
                  <CardDescription>
                    Secure your API requests with API keys
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-4">
                    All API requests require authentication using an API key passed in the Authorization header:
                  </p>
                  
                  <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm relative">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="absolute top-2 right-2 text-gray-400 hover:text-white"
                      onClick={() => copyToClipboard('Authorization: Bearer YOUR_API_KEY', 'auth')}
                    >
                      {copiedCode === 'auth' ? <CheckCircle2 className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                    <pre>Authorization: Bearer YOUR_API_KEY</pre>
                  </div>
                </CardContent>
              </Card>
            </motion.section>

            {/* API Endpoints */}
            <motion.section
              id="endpoints"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>API Endpoints</CardTitle>
                  <CardDescription>
                    Available endpoints for deepfake detection
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Analyze Endpoint */}
                  <div className="border-l-4 border-blue-500 pl-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className="bg-green-100 text-green-800">POST</Badge>
                      <code className="text-sm">/api/v1/analyze</code>
                    </div>
                    <p className="text-gray-600 mb-3">
                      Submit media for deepfake analysis. Returns a job ID for tracking progress.
                    </p>
                    
                    <h5 className="font-semibold mb-2">Request Body</h5>
                    <div className="bg-gray-50 p-3 rounded text-sm space-y-1">
                      <div><code>file</code> (multipart/form-data): Media file (MP4, MOV, JPG, PNG)</div>
                      <div><code>url</code> (string, optional): YouTube URL instead of file upload</div>
                    </div>
                  </div>

                  {/* Status Endpoint */}
                  <div className="border-l-4 border-yellow-500 pl-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className="bg-blue-100 text-blue-800">GET</Badge>
                      <code className="text-sm">/api/v1/status/{`{job_id}`}</code>
                    </div>
                    <p className="text-gray-600">
                      Check the current status of an analysis job.
                    </p>
                  </div>

                  {/* Results Endpoint */}
                  <div className="border-l-4 border-purple-500 pl-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className="bg-blue-100 text-blue-800">GET</Badge>
                      <code className="text-sm">/api/v1/results/{`{job_id}`}</code>
                    </div>
                    <p className="text-gray-600">
                      Retrieve the complete analysis results for a completed job.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.section>

            {/* Code Examples */}
            <motion.section
              id="examples"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Code Examples</CardTitle>
                  <CardDescription>
                    Implementation examples in popular programming languages
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="javascript" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="javascript">JavaScript</TabsTrigger>
                      <TabsTrigger value="python">Python</TabsTrigger>
                      <TabsTrigger value="curl">cURL</TabsTrigger>
                    </TabsList>

                    <TabsContent value="javascript" className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-3">Upload and Analyze File</h4>
                        <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm relative">
                          <Button
                            size="sm"
                            variant="ghost"
                            className="absolute top-2 right-2 text-gray-400 hover:text-white"
                            onClick={() => copyToClipboard(`const analyzeMedia = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('https://api.ifake.ai/v1/analyze', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY'
    },
    body: formData
  });

  const { job_id } = await response.json();
  return job_id;
};

// Check status
const checkStatus = async (jobId) => {
  const response = await fetch(\`https://api.ifake.ai/v1/status/\${jobId}\`, {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY'
    }
  });
  
  return await response.json();
};

// Get results
const getResults = async (jobId) => {
  const response = await fetch(\`https://api.ifake.ai/v1/results/\${jobId}\`, {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY'
    }
  });
  
  return await response.json();
};`, 'js-example')}
                          >
                            {copiedCode === 'js-example' ? <CheckCircle2 className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                          </Button>
                          <pre>{`const analyzeMedia = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('https://api.ifake.ai/v1/analyze', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY'
    },
    body: formData
  });

  const { job_id } = await response.json();
  return job_id;
};

// Check status
const checkStatus = async (jobId) => {
  const response = await fetch(\`https://api.ifake.ai/v1/status/\${jobId}\`, {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY'
    }
  });
  
  return await response.json();
};

// Get results
const getResults = async (jobId) => {
  const response = await fetch(\`https://api.ifake.ai/v1/results/\${jobId}\`, {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY'
    }
  });
  
  return await response.json();
};`}</pre>
                        </div>
                      </div>
                    </TabsContent>

                    <TabsContent value="python" className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-3">Python SDK Example</h4>
                        <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm relative">
                          <Button
                            size="sm"
                            variant="ghost"
                            className="absolute top-2 right-2 text-gray-400 hover:text-white"
                            onClick={() => copyToClipboard(`import requests
import time

class iFakeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.ifake.ai/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def analyze_file(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/analyze",
                headers=self.headers,
                files=files
            )
        return response.json()['job_id']
    
    def analyze_url(self, youtube_url):
        data = {'url': youtube_url}
        response = requests.post(
            f"{self.base_url}/analyze",
            headers=self.headers,
            json=data
        )
        return response.json()['job_id']
    
    def check_status(self, job_id):
        response = requests.get(
            f"{self.base_url}/status/{job_id}",
            headers=self.headers
        )
        return response.json()
    
    def get_results(self, job_id):
        response = requests.get(
            f"{self.base_url}/results/{job_id}",
            headers=self.headers
        )
        return response.json()
    
    def analyze_and_wait(self, file_path=None, url=None):
        # Submit for analysis
        if file_path:
            job_id = self.analyze_file(file_path)
        elif url:
            job_id = self.analyze_url(url)
        else:
            raise ValueError("Provide either file_path or url")
        
        # Wait for completion
        while True:
            status = self.check_status(job_id)
            if status['status'] == 'SUCCESS':
                return self.get_results(job_id)
            elif status['status'] == 'FAILED':
                raise Exception("Analysis failed")
            time.sleep(2)

# Usage
client = iFakeClient("YOUR_API_KEY")
results = client.analyze_and_wait(file_path="video.mp4")
print(f"Verdict: {results['verdict']}")
print(f"Confidence: {results['confidence']}%")`, 'python-example')}
                          >
                            {copiedCode === 'python-example' ? <CheckCircle2 className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                          </Button>
                          <pre>{`import requests
import time

class iFakeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.ifake.ai/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def analyze_file(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/analyze",
                headers=self.headers,
                files=files
            )
        return response.json()['job_id']
    
    def check_status(self, job_id):
        response = requests.get(
            f"{self.base_url}/status/{job_id}",
            headers=self.headers
        )
        return response.json()
    
    def get_results(self, job_id):
        response = requests.get(
            f"{self.base_url}/results/{job_id}",
            headers=self.headers
        )
        return response.json()

# Usage
client = iFakeClient("YOUR_API_KEY")
job_id = client.analyze_file("video.mp4")
results = client.get_results(job_id)`}</pre>
                        </div>
                      </div>
                    </TabsContent>

                    <TabsContent value="curl" className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-3">cURL Commands</h4>
                        <div className="space-y-4">
                          <div>
                            <h5 className="text-sm font-medium mb-2">Submit for analysis</h5>
                            <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm relative">
                              <Button
                                size="sm"
                                variant="ghost"
                                className="absolute top-2 right-2 text-gray-400 hover:text-white"
                                onClick={() => copyToClipboard(`curl -X POST https://api.ifake.ai/v1/analyze \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -F "file=@video.mp4"`, 'curl-analyze')}
                              >
                                {copiedCode === 'curl-analyze' ? <CheckCircle2 className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                              </Button>
                              <pre>{`curl -X POST https://api.ifake.ai/v1/analyze \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -F "file=@video.mp4"`}</pre>
                            </div>
                          </div>

                          <div>
                            <h5 className="text-sm font-medium mb-2">Check status</h5>
                            <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm relative">
                              <Button
                                size="sm"
                                variant="ghost"
                                className="absolute top-2 right-2 text-gray-400 hover:text-white"
                                onClick={() => copyToClipboard(`curl -X GET https://api.ifake.ai/v1/status/JOB_ID \\
  -H "Authorization: Bearer YOUR_API_KEY"`, 'curl-status')}
                              >
                                {copiedCode === 'curl-status' ? <CheckCircle2 className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                              </Button>
                              <pre>{`curl -X GET https://api.ifake.ai/v1/status/JOB_ID \\
  -H "Authorization: Bearer YOUR_API_KEY"`}</pre>
                            </div>
                          </div>
                        </div>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </motion.section>

            {/* Response Format */}
            <motion.section
              id="response-format"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Response Format</CardTitle>
                  <CardDescription>
                    Structure of API responses
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <h4 className="font-semibold mb-3">Analysis Results</h4>
                    <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm">
                      <pre>{`{
  "job_id": "abc123def456",
  "status": "SUCCESS",
  "verdict": "FAKE",
  "confidence": 87.3,
  "processing_time": 24.7,
  "analysis": {
    "face_detection": {
      "faces_found": 1,
      "confidence": 98.2
    },
    "spatial_analysis": {
      "artifacts_detected": true,
      "confidence": 85.7
    },
    "temporal_analysis": {
      "inconsistencies": true,
      "confidence": 91.4
    },
    "ensemble_score": 87.3
  },
  "metadata": {
    "file_size": "45.2MB",
    "duration": "2m 15s",
    "resolution": "1920x1080",
    "format": "mp4"
  }
}`}</pre>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-3">Status Response</h4>
                    <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm">
                      <pre>{`{
  "job_id": "abc123def456",
  "status": "PROCESSING",
  "progress": 65,
  "estimated_completion": "2024-01-15T10:30:00Z"
}`}</pre>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.section>

            {/* Rate Limits */}
            <motion.section
              id="rate-limits"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.7 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Rate Limits & Pricing</CardTitle>
                  <CardDescription>
                    Usage limits and pricing information
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3">Rate Limits</h4>
                      <ul className="space-y-2 text-sm text-gray-600">
                        <li>• <strong>Free Tier:</strong> 10 requests per day</li>
                        <li>• <strong>Basic Plan:</strong> 1,000 requests per month</li>
                        <li>• <strong>Pro Plan:</strong> 10,000 requests per month</li>
                        <li>• <strong>Enterprise:</strong> Custom limits</li>
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold mb-3">File Limits</h4>
                      <ul className="space-y-2 text-sm text-gray-600">
                        <li>• <strong>Max file size:</strong> 500MB</li>
                        <li>• <strong>Max duration:</strong> 30 minutes</li>
                        <li>• <strong>Supported formats:</strong> MP4, MOV, JPG, PNG</li>
                        <li>• <strong>Max resolution:</strong> 4K (3840x2160)</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.section>
          </div>
        </div>
      </div>
    </div>
  );
}