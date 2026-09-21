























import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { HeroCanvas } from "@/components/three/HeroCanvas";
import { toast } from 'sonner';
import { 
  Mail, Phone, MapPin, Send, Linkedin, Users, MessageCircle, 
  Building, Clock, CheckCircle2, GraduationCap, Star, Award, BookOpen, AlertTriangle 
} from 'lucide-react';

const teamMembers = [
  {
    id: 1,
    name: "Shadabur Rahaman",
    role: "Team Lead & Core Developer",
    initials: "SR",
    email: "rahamanshadabur@gmail.com",
    linkedin: "https://www.linkedin.com/in/shadabur-rahaman-1b5703249",
    bio: "Leading the development of iFake's MesoNet CNN-powered deepfake detection system",
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
    bio: "Crafting intuitive user interfaces and seamless user experiences for iFake platform",
    specialization: "React.js & Design Systems"
  },
  {
    id: 3,
    name: "Vanishree M",
    role: "AI Research & Data Scientist",
    initials: "VM",
    email: "vanishreem2004@gmail.com",
    linkedin: "https://www.linkedin.com/in/vanishree-m-293963306",
    bio: "Researching and implementing advanced MesoNet CNN deepfake detection algorithms",
    specialization: "Computer Vision & Neural Networks"
  },
  {
    id: 4,
    name: "Hithaishi U",
    role: "Quality Assurance & Testing",
    initials: "HU",
    email: "hithaishiugowda@gmail.com",
    linkedin: "https://www.linkedin.com/in/hithaishi-u-b281672b1",
    bio: "Ensuring robust performance and reliability of the MesoNet detection system",
    specialization: "Software Testing & Validation"
  }
];

const projectGuide = {
  name: "Mrs. Ayisha Khanum",
  role: "Project Coordinator & Guide",
  initials: "AK",
  email: "ayisha.k@example.com",
  linkedin: "https://linkedin.com/in/ayishakhanum",
  bio: "Mentoring and guiding the development of innovative AI solutions for deepfake detection",
  department: "Department of Computer Science & Engineering"
};

const contactInfo = [
  {
    icon: Mail,
    title: 'Email',
    content: 'rahamanshadabur@gmail.com',
    description: 'General inquiries and support'
  },
  {
    icon: Building,
    title: 'Department',
    content: 'Computer Science & Engineering',
    description: 'University Final Year Project'
  },
  {
    icon: Clock,
    title: 'Response Time',
    content: '24-48 hours',
    description: 'Academic project timeline'
  }
];

const Contact: React.FC = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    subject: '',
    regarding: '',
    message: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  // Enhanced validation function
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Name validation
    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    } else if (formData.fullName.trim().length < 2) {
      newErrors.fullName = 'Name must be at least 2 characters';
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email address is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Subject validation
    if (!formData.subject.trim()) {
      newErrors.subject = 'Subject is required';
    } else if (formData.subject.trim().length < 5) {
      newErrors.subject = 'Subject must be at least 5 characters';
    }

    // Regarding validation
    if (!formData.regarding) {
      newErrors.regarding = 'Please select a topic';
    }

    // Message validation
    if (!formData.message.trim()) {
      newErrors.message = 'Message is required';
    } else if (formData.message.trim().length < 10) {
      newErrors.message = 'Message must be at least 10 characters';
    } else if (formData.message.trim().length > 500) {
      newErrors.message = 'Message cannot exceed 500 characters';
    }

    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    
    const formErrors = validateForm();
    
    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors);
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Import contact service dynamically to avoid circular dependencies
      const { default: contactService } = await import('@/services/contactService');
      
      // Submit contact form
      const response = await contactService.submitContactForm(formData);
      
      setIsSubmitted(true);
      setFormData({ fullName: '', email: '', subject: '', regarding: '', message: '' });
      
      // Show success message with request ID
      if (response.requestId) {
        toast.success(`Message sent successfully! Request ID: ${response.requestId}`);
      } else {
        toast.success('Message sent successfully!');
      }
    } catch (error) {
      console.error('Contact form submission error:', error);
      setErrors({ submit: error.message || 'Failed to send message. Please try again.' });
      toast.error('Failed to send message. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <main>
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-background">
        {/* 3D Background */}
        <HeroCanvas className="absolute inset-0 w-full h-full" />
        
        {/* Hero Content */}
        <div className="relative z-10 container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-hero font-bold mb-6 gradient-text neural-text">
              Contact Us
            </h1>
            <p className="text-xl text-muted-foreground neural-text max-w-3xl mx-auto mb-8">
              Get in touch with the undergraduate team behind iFake - an innovative MesoNet CNN-powered 
              deepfake detection system developed under academic mentorship.
            </p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <Badge variant="secondary" className="neural-card bg-success/10 text-success border-success/20 hover:bg-success/20 transition-colors">
                <Mail className="w-3 h-3 mr-1" />
                Response within 24-48 hours
              </Badge>
            </motion.div>
            
            {/* Live Animation Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto mt-12"
            >
              <motion.div 
                className="text-center"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <div className="text-3xl font-bold text-ai-core mb-2">4</div>
                <div className="text-sm text-muted-foreground">Team Members</div>
              </motion.div>
              <motion.div 
                className="text-center"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <div className="text-3xl font-bold text-ai-neural mb-2">24-48h</div>
                <div className="text-sm text-muted-foreground">Response Time</div>
              </motion.div>
              <motion.div 
                className="text-center"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <div className="text-3xl font-bold text-ai-data mb-2">100%</div>
                <div className="text-sm text-muted-foreground">Academic Project</div>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-hero pointer-events-none" />
      </section>

      <div className="container mx-auto max-w-6xl px-4 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-20">
          {/* Contact Form */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card className="neural-card p-8 hover-lift">
              <CardHeader className="px-0 pt-0">
                <CardTitle className="text-2xl mb-2 neural-text">Send us a message</CardTitle>
                <p className="text-muted-foreground neural-text">
                  Whether you have questions about our MesoNet CNN system, need technical support, 
                  or want to discuss research collaboration, we'd love to hear from you.
                </p>
              </CardHeader>
              <CardContent className="px-0">
                {isSubmitted ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-8"
                  >
                    <div className="w-16 h-16 rounded-full bg-success/10 flex items-center justify-center mx-auto mb-4 neural-glow">
                      <Send className="w-8 h-8 text-success" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2 neural-text">Message sent!</h3>
                    <p className="text-muted-foreground neural-text mb-4">
                      Thank you for reaching out to our iFake development team. We'll get back to you within 24-48 hours.
                    </p>
                    <Button
                      onClick={() => setIsSubmitted(false)}
                      variant="outline"
                      className="neural-button hover-lift"
                    >
                      Send Another Message
                    </Button>
                  </motion.div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {errors.submit && (
                      <div className="neural-card p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-destructive" />
                        <span className="text-destructive neural-text">{errors.submit}</span>
                      </div>
                    )}

                    <div className="space-y-2">
                      <Label htmlFor="fullName" className="neural-text">Full Name *</Label>
                      <Input
                        id="fullName"
                        name="fullName"
                        value={formData.fullName}
                        onChange={(e) => handleInputChange('fullName', e.target.value)}
                        placeholder="Your full name"
                        className={`neural-input ${errors.fullName ? 'border-destructive' : ''}`}
                      />
                      {errors.fullName && (
                        <p className="text-sm text-destructive flex items-center gap-1 neural-text">
                          <AlertTriangle className="w-4 h-4" />
                          {errors.fullName}
                        </p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email" className="neural-text">Email Address *</Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        placeholder="your@email.com"
                        className={`neural-input ${errors.email ? 'border-destructive' : ''}`}
                      />
                      {errors.email && (
                        <p className="text-sm text-destructive flex items-center gap-1 neural-text">
                          <AlertTriangle className="w-4 h-4" />
                          {errors.email}
                        </p>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="subject" className="neural-text">Subject *</Label>
                        <Input
                          id="subject"
                          name="subject"
                          value={formData.subject}
                          onChange={(e) => handleInputChange('subject', e.target.value)}
                          placeholder="What's this about?"
                          className={`neural-input ${errors.subject ? 'border-destructive' : ''}`}
                        />
                        {errors.subject && (
                          <p className="text-sm text-destructive flex items-center gap-1 neural-text">
                            <AlertTriangle className="w-4 h-4" />
                            {errors.subject}
                          </p>
                        )}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="regarding" className="neural-text">Regarding *</Label>
                        <select
                          id="regarding"
                          value={formData.regarding}
                          onChange={(e) => handleInputChange('regarding', e.target.value)}
                          className={`neural-input flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
                            errors.regarding ? 'border-destructive' : ''
                          }`}
                        >
                          <option value="">Select a topic</option>
                          <option value="technical">Technical Support</option>
                          <option value="collaboration">Research Collaboration</option>
                          <option value="feedback">Feedback & Suggestions</option>
                          <option value="academic">Academic Inquiry</option>
                          <option value="mesonet">MesoNet CNN Questions</option>
                          <option value="other">Other</option>
                        </select>
                        {errors.regarding && (
                          <p className="text-sm text-destructive flex items-center gap-1 neural-text">
                            <AlertTriangle className="w-4 h-4" />
                            {errors.regarding}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="message" className="neural-text">Message * ({formData.message.length}/500)</Label>
                      <Textarea
                        id="message"
                        name="message"
                        value={formData.message}
                        onChange={(e) => handleInputChange('message', e.target.value)}
                        placeholder="Tell us more about your inquiry..."
                        rows={5}
                        maxLength={500}
                        className={`neural-input ${errors.message ? 'border-destructive' : ''}`}
                      />
                      {errors.message && (
                        <p className="text-sm text-destructive flex items-center gap-1 neural-text">
                          <AlertTriangle className="w-4 h-4" />
                          {errors.message}
                        </p>
                      )}
                    </div>

                    <Button
                      type="submit"
                      size="lg"
                      className="neural-button w-full glow-primary hover-lift"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                          Sending...
                        </>
                      ) : (
                        <>
                          <Send className="w-5 h-5 mr-2" />
                          Send Message
                        </>
                      )}
                    </Button>
                  </form>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Contact Information */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="space-y-6"
          >
            <div>
              <h2 className="text-2xl font-bold mb-6 neural-text">Get in touch</h2>
              <div className="space-y-6">
                {contactInfo.map((contact, index) => (
                  <motion.div
                    key={contact.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="neural-card flex space-x-4 p-4 rounded-lg hover-lift"
                  >
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center flex-shrink-0 neural-glow">
                      <contact.icon className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold mb-1 neural-text">{contact.title}</h3>
                      <p className="font-mono text-sm mb-1 neural-text">{contact.content}</p>
                      <p className="text-sm text-muted-foreground neural-text">{contact.description}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Project Guide Card */}
            <Card className="neural-card p-6 hover-lift">
              <CardContent className="px-0">
                <h3 className="font-semibold mb-3 flex items-center gap-2 neural-text">
                  <div className="w-6 h-6 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                    <GraduationCap className="w-3 h-3 text-primary" />
                  </div>
                  Project Guide
                </h3>
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center text-primary font-bold neural-glow">
                    {projectGuide.initials}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold neural-text">{projectGuide.name}</h4>
                    <Badge variant="secondary" className="neural-card mb-2">
                      {projectGuide.role}
                    </Badge>
                    <p className="text-sm text-muted-foreground neural-text mb-2">{projectGuide.department}</p>
                    <p className="text-sm mb-3 neural-text">{projectGuide.bio}</p>
                    <div className="flex items-center gap-3">
                      <a 
                        href={`mailto:${projectGuide.email}`}
                        className="text-primary hover:text-primary/80 neural-button p-2 rounded-lg hover:bg-primary/10 transition-colors"
                      >
                        <Mail className="w-4 h-4" />
                      </a>
                      <a 
                        href={projectGuide.linkedin}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:text-primary/80 neural-button p-2 rounded-lg hover:bg-primary/10 transition-colors"
                      >
                        <Linkedin className="w-4 h-4" />
                      </a>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="neural-card p-6 bg-gradient-to-br from-primary/10 via-accent/10 to-primary/10 text-foreground hover-lift">
              <CardContent className="px-0">
                <h3 className="font-semibold mb-3 neural-text">About iFake</h3>
                <p className="text-muted-foreground neural-text text-sm mb-4">
                  iFake is our undergraduate capstone project focused on developing advanced MesoNet CNN-powered 
                  deepfake detection technology. We're passionate about contributing to digital media authenticity.
                </p>
                <Button variant="secondary" size="sm" className="neural-button hover-lift">
                  Learn More
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Team Section */}
        <section>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-section font-bold mb-6 neural-text">Meet Our Team</h2>
            <p className="text-lg text-muted-foreground neural-text max-w-3xl mx-auto">
              Our diverse team of researchers, engineers, and AI specialists are dedicated to advancing 
              the state of deepfake detection through MesoNet CNN technology.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {teamMembers.map((member, index) => (
              <motion.div
                key={member.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="neural-card text-center hover-lift transition-all duration-300">
                  <CardHeader className="pb-4">
                    <div className={`w-24 h-24 rounded-full ${
                      member.isLead ? 'bg-gradient-to-br from-primary/20 to-accent/20' : 'bg-gradient-to-br from-accent/20 to-primary/20'
                    } flex items-center justify-center mx-auto mb-4 text-primary text-2xl font-bold neural-glow`}>
                      {member.initials}
                    </div>
                    <CardTitle className="text-lg neural-text">{member.name}</CardTitle>
                    <Badge variant={member.isLead ? "default" : "secondary"} className={`mx-auto ${member.isLead ? "bg-primary text-primary-foreground" : "neural-card"}`}>
                      {member.role}
                    </Badge>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground neural-text mb-2">{member.specialization}</p>
                    <p className="text-sm text-muted-foreground neural-text leading-relaxed mb-4">
                      {member.bio}
                    </p>
                    <div className="flex items-center justify-center space-x-3">
                      <Button variant="ghost" size="sm" className="neural-button w-8 h-8 p-0 hover:bg-primary/10" asChild>
                        <a href={`mailto:${member.email}`}>
                          <Mail className="w-4 h-4" />
                        </a>
                      </Button>
                      <Button variant="ghost" size="sm" className="neural-button w-8 h-8 p-0 hover:bg-primary/10" asChild>
                        <a href={member.linkedin} target="_blank" rel="noopener noreferrer">
                          <Linkedin className="w-4 h-4" />
                        </a>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
};

export default Contact;
