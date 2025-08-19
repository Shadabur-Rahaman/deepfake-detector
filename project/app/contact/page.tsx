"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  Mail, 
  Phone, 
  MapPin, 
  Send,
  Linkedin,
  Users,
  MessageCircle,
  Building,
  Clock,
  CheckCircle2,
  GraduationCap,
  Star,
  Award,
  BookOpen
} from 'lucide-react';

const teamMembers = [
  {
    id: 1,
    name: "Shadabur Rahaman",
    role: "Team Lead & Core Developer",
    initials: "SR",
    email: "rahamanshadabur@gmail.com",
    linkedin: "https://www.linkedin.com/in/shadabur-rahaman-1b5703249",
    bio: "Leading the development of iFake's AI-powered deepfake detection system",
    specialization: "Machine Learning & Backend Development",
    isLead: true
  },
  {
    id: 2,
    name: "Sushmitha M J",
    role: "Frontend Developer & UI/UX Designer",
    initials: "SM",
    email: "2004sushmithamjayappa@gmail.com",
    linkedin: "https://www.linkedin.com/in/sushmitha-m-j-2024842a6",
    bio: "Crafting intuitive user interfaces and seamless user experiences",
    specialization: "React.js & Design Systems"
  },
  {
    id: 3,
    name: "Vanishree M",
    role: "AI Research & Data Scientist",
    initials: "VM",
    email: "vanishreem2004@gmail.com",
    linkedin: "https://www.linkedin.com/in/vanishree-m-293963306",
    bio: "Researching and implementing advanced deepfake detection algorithms",
    specialization: "Computer Vision & Neural Networks"
  },
  {
    id: 4,
    name: "Hithaishi U",
    role: "Quality Assurance & Testing",
    initials: "HU",
    email: "hithaishiugowda@gmail.com",
    linkedin: "https://www.linkedin.com/in/hithaishi-u-b281672b1",
    bio: "Ensuring robust performance and reliability of the detection system",
    specialization: "Software Testing & Validation"
  }
];

const projectGuide = {
  name: "Mrs. Ayisha Khanum",
  role: "Project Coordinator & Guide",
  initials: "AK",
  email: "ayisha.k@example.com",
  linkedin: "https://linkedin.com/in/ayishakhanum",
  bio: "Mentoring and guiding the development of innovative AI solutions",
  department: "Department of Computer Science & Engineering"
};

export default function Contact() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    subject: '',
    regarding: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsSubmitting(false);
    setIsSubmitted(true);
    setFormData({
      fullName: '',
      email: '',
      subject: '',
      regarding: '',
      message: ''
    });
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          className="text-center space-y-6 px-6"
        >
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-10 h-10 text-green-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900">Message Sent Successfully!</h1>
          <p className="text-xl text-gray-600 max-w-md mx-auto">
            Thank you for reaching out to our iFake development team. We'll get back to you within 24 hours.
          </p>
          <Button onClick={() => setIsSubmitted(false)} className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
            Send Another Message
          </Button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* No navigation here - it's handled by the global layout */}
      
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center space-y-6 mb-16"
        >
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200">
            <GraduationCap className="h-4 w-4 text-blue-600 mr-2" />
            <span className="text-blue-800 text-sm font-medium">University Project Team</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900">
            Meet Our Team
          </h1>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Get in touch with the undergraduate team behind iFake - an innovative AI-powered deepfake detection system developed under academic mentorship.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-16">
          {/* Contact Form */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <Card className="border-gray-200 bg-white shadow-lg">
              <CardHeader className="pb-6 border-b border-gray-100">
                <CardTitle className="text-gray-900 text-2xl font-semibold flex items-center">
                  <MessageCircle className="mr-3 h-6 w-6 text-blue-600" />
                  Contact Our Team
                </CardTitle>
                <CardDescription className="text-gray-600 text-base">
                  Have questions about our deepfake detection research? Want to collaborate or learn more about our project? We'd love to hear from you!
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="fullName" className="text-gray-900">Full Name</Label>
                      <Input
                        id="fullName"
                        value={formData.fullName}
                        onChange={(e) => handleInputChange('fullName', e.target.value)}
                        placeholder="Enter your full name"
                        required
                        className="h-12"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-gray-900">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        placeholder="Enter your email"
                        required
                        className="h-12"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="subject" className="text-gray-900">Subject</Label>
                    <Input
                      id="subject"
                      value={formData.subject}
                      onChange={(e) => handleInputChange('subject', e.target.value)}
                      placeholder="What's this about?"
                      required
                      className="h-12"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="regarding" className="text-gray-900">Regarding</Label>
                    <Select value={formData.regarding} onValueChange={(value) => handleInputChange('regarding', value)}>
                      <SelectTrigger className="h-12">
                        <SelectValue placeholder="Select a topic" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="project-inquiry">Project Inquiry</SelectItem>
                        <SelectItem value="collaboration">Academic Collaboration</SelectItem>
                        <SelectItem value="technical-support">Technical Questions</SelectItem>
                        <SelectItem value="research-collaboration">Research Partnership</SelectItem>
                        <SelectItem value="demo-request">Demo Request</SelectItem>
                        <SelectItem value="feedback">Feedback & Suggestions</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="message" className="text-gray-900">Message</Label>
                    <Textarea
                      id="message"
                      value={formData.message}
                      onChange={(e) => handleInputChange('message', e.target.value)}
                      placeholder="Tell us more about your inquiry..."
                      required
                      rows={6}
                      className="resize-none"
                    />
                  </div>

                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full h-14 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-3" />
                        Sending Message...
                      </>
                    ) : (
                      <>
                        <Send className="mr-3 h-5 w-5" />
                        Send Message
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </motion.div>

          {/* Team Information */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="space-y-8"
          >
            {/* Project Guide */}
            <Card className="border-gray-200 bg-white shadow-lg">
              <CardHeader className="pb-6 border-b border-gray-100">
                <CardTitle className="text-gray-900 text-2xl font-semibold flex items-center">
                  <Award className="mr-3 h-6 w-6 text-purple-600" />
                  Project Mentor
                </CardTitle>
                <CardDescription className="text-gray-600">
                  Academic guidance and project coordination
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-8">
                <div className="flex items-start space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                    {projectGuide.initials}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-lg">{projectGuide.name}</h3>
                    <p className="text-purple-600 font-medium mb-2">{projectGuide.role}</p>
                    <p className="text-sm text-gray-600 mb-2">{projectGuide.department}</p>
                    <p className="text-sm text-gray-600 leading-relaxed mb-4">{projectGuide.bio}</p>
                    <div className="flex space-x-3">
                      <a 
                        href={`mailto:${projectGuide.email}`}
                        className="p-2 text-gray-400 hover:text-purple-600 transition-colors"
                      >
                        <Mail className="h-5 w-5" />
                      </a>
                      <a 
                        href={projectGuide.linkedin}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-gray-400 hover:text-purple-600 transition-colors"
                      >
                        <Linkedin className="h-5 w-5" />
                      </a>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Development Team */}
            <Card className="border-gray-200 bg-white shadow-lg">
              <CardHeader className="pb-6 border-b border-gray-100">
                <CardTitle className="text-gray-900 text-2xl font-semibold flex items-center">
                  <Users className="mr-3 h-6 w-6 text-blue-600" />
                  Development Team
                </CardTitle>
                <CardDescription className="text-gray-600">
                  Undergraduate students building the future of AI-powered content verification
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-8">
                <div className="space-y-6">
                  {teamMembers.map((member, index) => (
                    <motion.div
                      key={member.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.6, delay: index * 0.1 }}
                      className={`relative p-4 rounded-lg border transition-all duration-300 hover:shadow-md ${
                        member.isLead 
                          ? 'bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200' 
                          : 'bg-gray-50 border-gray-200 hover:bg-white'
                      }`}
                    >
                      {member.isLead && (
                        <div className="absolute top-2 right-2">
                          <Star className="h-5 w-5 text-yellow-500" />
                        </div>
                      )}
                      <div className="flex items-start space-x-4">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold ${
                          member.isLead 
                            ? 'bg-gradient-to-r from-blue-500 to-purple-500' 
                            : 'bg-gradient-to-r from-gray-500 to-gray-600'
                        }`}>
                          {member.initials}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <h3 className="font-semibold text-gray-900">{member.name}</h3>
                            {member.isLead && (
                              <Badge className="bg-blue-100 text-blue-800 border-blue-200 text-xs">
                                Team Lead
                              </Badge>
                            )}
                          </div>
                          <p className="text-blue-600 font-medium text-sm mb-1">{member.role}</p>
                          <p className="text-xs text-purple-600 font-medium mb-2">{member.specialization}</p>
                          <p className="text-xs text-gray-600 leading-relaxed mb-3">{member.bio}</p>
                          <div className="flex space-x-2">
                            <a 
                              href={`mailto:${member.email}`}
                              className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                            >
                              <Mail className="h-4 w-4" />
                            </a>
                            <a 
                              href={member.linkedin}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                            >
                              <Linkedin className="h-4 w-4" />
                            </a>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Project Information */}
            <Card className="border-gray-200 bg-white shadow-lg">
              <CardHeader className="pb-6 border-b border-gray-100">
                <CardTitle className="text-gray-900 text-2xl font-semibold flex items-center">
                  <BookOpen className="mr-3 h-6 w-6 text-green-600" />
                  Project Details
                </CardTitle>
                <CardDescription className="text-gray-600">
                  Academic project information and contact details
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-8 space-y-6">
                <div className="flex items-start space-x-4">
                  <Building className="h-5 w-5 text-blue-600 mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Institution</h4>
                    <p className="text-gray-600 text-sm leading-relaxed">
                      Department of Computer Science & Engineering<br />
                      University Undergraduate Final Year Project<br />
                      Academic Year 2025-2026
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <Mail className="h-5 w-5 text-blue-600 mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Project Email</h4>
                    <p className="text-gray-600 text-sm">
                      <a href="mailto:ifake.project@university.edu" className="hover:text-blue-600 transition-colors">
                        ifake.project@university.edu
                      </a>
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <Clock className="h-5 w-5 text-blue-600 mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Response Time</h4>
                    <p className="text-gray-600 text-sm leading-relaxed">
                      We typically respond within 24-48 hours<br />
                      For urgent inquiries, please contact our team lead directly
                    </p>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <GraduationCap className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold text-blue-800 mb-1">About This Project</h4>
                      <p className="text-blue-700 text-sm leading-relaxed">
                        iFake is our undergraduate capstone project focused on developing advanced AI-powered deepfake detection technology. 
                        We're passionate about contributing to digital media authenticity and combating misinformation through innovative machine learning solutions.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
