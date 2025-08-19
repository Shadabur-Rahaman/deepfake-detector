"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Code, 
  Key, 
  Zap,
  CheckCircle2,
  AlertCircle,
  Copy,
  ExternalLink,
  Book,
  Shield,
  Clock,
  Globe,
  Server,
  Database
} from 'lucide-react';
import Link from 'next/link';

const pricingPlans = [
  {
    name: "Starter",
    price: "Free",
    description: "Perfect for testing and small projects",
    requests: "1,000 requests/month",
    features: [
      "Basic deepfake detection",
      "Image & video analysis",
      "REST API access",
      "Community support",
      "Rate limiting: 10 req/min"
    ],
    buttonText: "Get Started Free",
    popular: false
  },
  {
    name: "Professional",
    price: "$49",
    description: "Ideal for growing businesses",
    requests: "50,000 requests/month",
    features: [
      "Advanced detection models",
      "Batch processing",
      "Priority support",
      "Custom webhooks",
      "Rate limiting: 100 req/min",
      "99.9% uptime SLA"
    ],
    buttonText: "Start Free Trial",
    popular: true
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For large scale deployments",
    requests: "Unlimited requests",
    features: [
      "On-premise deployment",
      "Custom model training",
      "24/7 dedicated support",
      "Custom integrations",
      "No rate limiting",
      "99.99% uptime SLA"
    ],
    buttonText: "Contact Sales",
    popular: false
  }
];

const codeExamples = {
  curl: `curl -X POST "https://api.ifake.ai/v1/detect" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@path/to/your/video.mp4" \\
  -F "options={\\"return_confidence\\": true}"`,
  
  python: `import requests

# Upload and analyze media
url = "https://api.ifake.ai/v1/detect"
headers = {
    "Authorization": "Bearer YOUR_API_KEY"
}

files = {
    "file": open("path/to/your/video.mp4", "rb")
}

data = {
    "options": '{"return_confidence": true}'
}

response = requests.post(url, headers=headers, files=files, data=data)
result = response.json()

print(f"Result: {result['prediction']}")
print(f"Confidence: {result['confidence']}%")`,

  javascript: `const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('options', JSON.stringify({
  return_confidence: true
}));

const response = await fetch('https://api.ifake.ai/v1/detect', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY'
  },
  body: formData
});

const result = await response.json();
console.log('Prediction:', result.prediction);
console.log('Confidence:', result.confidence + '%');`,

  node: `const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('file', fs.createReadStream('path/to/your/video.mp4'));
form.append('options', JSON.stringify({ return_confidence: true }));

try {
  const response = await axios.post('https://api.ifake.ai/v1/detect', form, {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY',
      ...form.getHeaders()
    }
  });
  
  console.log('Result:', response.data);
} catch (error) {
  console.error('Error:', error.response.data);
}`
};

export default function APIPage() {
  const [activeExample, setActiveExample] = useState('curl');
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const copyToClipboard = (code: string, type: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(type);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Navigation */}

      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center space-y-6 mb-16"
        >
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200">
            <Code className="h-4 w-4 text-blue-600 mr-2" />
            <span className="text-blue-800 text-sm font-medium">Developer API</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900">
            Powerful Detection API
          </h1>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Integrate advanced deepfake detection into your applications with our simple, fast, and reliable API
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8">
              <Link href="#get-started">Get API Key</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="border-gray-300 text-gray-700">
              <Link href="#documentation">View Documentation</Link>
            </Button>
          </div>
        </motion.div>

        {/* API Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16"
        >
          {[
            { label: "API Uptime", value: "99.9%", icon: <Server className="h-5 w-5" /> },
            { label: "Avg Response", value: "< 2s", icon: <Clock className="h-5 w-5" /> },
            { label: "Daily Requests", value: "1M+", icon: <Database className="h-5 w-5" /> },
            { label: "Global CDN", value: "150+ Regions", icon: <Globe className="h-5 w-5" /> }
          ].map((stat, index) => (
            <Card key={index} className="border-gray-200 bg-white shadow-sm text-center">
              <CardContent className="p-6">
                <div className="flex justify-center mb-3 text-blue-600">
                  {stat.icon}
                </div>
                <div className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </CardContent>
            </Card>
          ))}
        </motion.div>

        {/* Quick Start */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mb-16"
        >
          <Card className="border-gray-200 bg-white shadow-lg">
            <CardHeader className="border-b border-gray-100">
              <CardTitle className="text-gray-900 text-2xl font-semibold">Quick Start</CardTitle>
              <CardDescription className="text-gray-600">
                Get up and running with iFake API in minutes
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-8">
              <Tabs value={activeExample} onValueChange={setActiveExample}>
                <div className="flex flex-col lg:flex-row gap-8">
                  <div className="lg:w-1/3">
                    <TabsList className="grid w-full grid-cols-2 lg:grid-cols-1 lg:h-auto bg-gray-100">
                      <TabsTrigger value="curl" className="data-[state=active]:bg-white justify-start">
                        cURL
                      </TabsTrigger>
                      <TabsTrigger value="python" className="data-[state=active]:bg-white justify-start">
                        Python
                      </TabsTrigger>
                      <TabsTrigger value="javascript" className="data-[state=active]:bg-white justify-start">
                        JavaScript
                      </TabsTrigger>
                      <TabsTrigger value="node" className="data-[state=active]:bg-white justify-start">
                        Node.js
                      </TabsTrigger>
                    </TabsList>
                  </div>
                  
                  <div className="lg:w-2/3">
                    {Object.entries(codeExamples).map(([key, code]) => (
                      <TabsContent key={key} value={key} className="mt-0">
                        <div className="relative">
                          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                            <code>{code}</code>
                          </pre>
                          <Button
                            size="sm"
                            variant="outline"
                            className="absolute top-2 right-2 bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700"
                            onClick={() => copyToClipboard(code, key)}
                          >
                            {copiedCode === key ? (
                              <CheckCircle2 className="h-3 w-3" />
                            ) : (
                              <Copy className="h-3 w-3" />
                            )}
                          </Button>
                        </div>
                      </TabsContent>
                    ))}
                  </div>
                </div>
              </Tabs>
            </CardContent>
          </Card>
        </motion.div>

        {/* API Endpoints */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-8">API Endpoints</h2>
          <div className="space-y-6">
            {[
              {
                method: "POST",
                endpoint: "/v1/detect",
                description: "Analyze media file for deepfake content",
                parameters: ["file (multipart)", "options (JSON)"],
                response: "Detection result with confidence score"
              },
              {
                method: "GET",
                endpoint: "/v1/status/{job_id}",
                description: "Check analysis status for async requests",
                parameters: ["job_id (string)"],
                response: "Processing status and results"
              },
              {
                method: "GET",
                endpoint: "/v1/models",
                description: "List available detection models",
                parameters: ["None"],
                response: "Array of available models"
              },
              {
                method: "POST",
                endpoint: "/v1/batch",
                description: "Submit multiple files for batch processing",
                parameters: ["files (array)", "callback_url (string)"],
                response: "Batch job ID and tracking information"
              }
            ].map((endpoint, index) => (
              <Card key={index} className="border-gray-200 bg-white shadow-sm">
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row md:items-center gap-4">
                    <div className="flex items-center space-x-3">
                      <Badge 
                        variant="outline" 
                        className={`${
                          endpoint.method === 'POST' ? 'bg-green-100 text-green-800 border-green-200' : 
                          'bg-blue-100 text-blue-800 border-blue-200'
                        }`}
                      >
                        {endpoint.method}
                      </Badge>
                      <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                        {endpoint.endpoint}
                      </code>
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-700 font-medium mb-2">{endpoint.description}</p>
                      <div className="text-sm text-gray-600">
                        <span className="font-medium">Parameters:</span> {endpoint.parameters.join(", ")}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </motion.div>

        {/* Pricing Plans */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          id="get-started"
          className="mb-16"
        >
          <div className="text-center space-y-6 mb-12">
            <h2 className="text-3xl font-bold text-gray-900">API Pricing</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Choose the plan that fits your needs. All plans include our core detection features.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <Card 
                key={index} 
                className={`border-2 ${
                  plan.popular 
                    ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-purple-50' 
                    : 'border-gray-200 bg-white'
                } shadow-lg relative`}
              >
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                    Most Popular
                  </Badge>
                )}
                <CardHeader className="text-center pb-4">
                  <CardTitle className="text-2xl font-bold text-gray-900">{plan.name}</CardTitle>
                  <div className="space-y-2">
                    <div className="text-4xl font-bold text-gray-900">
                      {plan.price}
                      {plan.price !== "Free" && plan.price !== "Custom" && (
                        <span className="text-lg font-normal text-gray-600">/month</span>
                      )}
                    </div>
                    <p className="text-gray-600">{plan.description}</p>
                    <p className="text-sm font-medium text-blue-600">{plan.requests}</p>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center space-x-3">
                        <CheckCircle2 className="h-4 w-4 text-green-600 flex-shrink-0" />
                        <span className="text-gray-700 text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button 
                    className={`w-full ${
                      plan.popular 
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' 
                        : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                    variant={plan.popular ? 'default' : 'outline'}
                  >
                    {plan.buttonText}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </motion.div>

        {/* Documentation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          id="documentation"
        >
          <Card className="border-gray-200 bg-white shadow-lg">
            <CardHeader className="border-b border-gray-100">
              <CardTitle className="text-gray-900 text-2xl font-semibold flex items-center">
                <Book className="mr-3 h-6 w-6 text-blue-600" />
                Documentation & Resources
              </CardTitle>
              <CardDescription className="text-gray-600">
                Everything you need to integrate iFake API successfully
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-8">
              <div className="grid md:grid-cols-2 gap-6">
                {[
                  {
                    title: "API Reference",
                    description: "Complete API documentation with examples",
                    icon: <Code className="h-5 w-5" />,
                    link: "#"
                  },
                  {
                    title: "Authentication Guide",
                    description: "Learn how to authenticate your API requests",
                    icon: <Key className="h-5 w-5" />,
                    link: "#"
                  },
                  {
                    title: "Rate Limiting",
                    description: "Understanding API limits and best practices",
                    icon: <Shield className="h-5 w-5" />,
                    link: "#"
                  },
                  {
                    title: "SDKs & Libraries",
                    description: "Official SDKs for popular programming languages",
                    icon: <Zap className="h-5 w-5" />,
                    link: "#"
                  }
                ].map((resource, index) => (
                  <div key={index} className="flex items-start space-x-4 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="bg-blue-100 p-2 rounded-lg">
                      {resource.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-2">{resource.title}</h3>
                      <p className="text-gray-600 text-sm mb-3">{resource.description}</p>
                      <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700 p-0 h-auto">
                        Learn more <ExternalLink className="h-3 w-3 ml-1" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
