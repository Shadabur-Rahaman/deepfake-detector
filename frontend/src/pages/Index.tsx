import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { HeroCanvas } from "@/components/three/HeroCanvas"
import { HowIFakeThinks } from "@/components/HowIFakeThinks"
import { PerfMetrics } from "@/components/PerfMetrics"
import { ArrowRight, Play, Shield, Zap, Users, Globe } from "lucide-react"

const Index = () => {
  return (
    <main className="relative min-h-screen overflow-hidden">
      {/* 3D Background - Full Page */}
      <HeroCanvas className="absolute inset-0 w-full h-full z-0" />
      
      {/* Subtle background overlay for better readability */}
      <div className="absolute inset-0 bg-background/10 backdrop-blur-[0.5px] z-5" />
      
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center bg-background/60 backdrop-blur-sm">
        {/* Dedicated 3D Background for Hero Section */}
        <HeroCanvas className="absolute inset-0 w-full h-full z-0" />
        
        {/* Hero Content */}
        <div className="relative z-10 container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <Badge 
              variant="secondary" 
              className="mb-6 bg-primary/10 text-primary border-primary/20"
            >
              <Zap className="w-3 h-3 mr-1" />
              Powered by MesoNet CNN
            </Badge>
            
            <h1 className="text-hero font-bold mb-6 gradient-text leading-tight">
              Detect Deepfakes
              <br />
              <span className="text-ai-core">Instantly</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
              Advanced MesoNet CNN and FastAPI technology that identifies manipulated media with 
              <span className="text-success font-semibold"> 94.1% accuracy</span>.
              Real-time WebSocket analysis and YouTube URL processing.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
              <Button size="lg" className="glow-primary group" asChild>
                <Link to="/detection">
                  <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
                  Try Live Detection
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link to="/features">
                  <Shield className="w-5 h-5 mr-2" />
                  View Features
                </Link>
              </Button>
            </div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto"
            >
              <div className="text-center">
                <div className="text-3xl font-bold text-ai-core">94.1%</div>
                <div className="text-sm text-muted-foreground">MesoNet Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-ai-neural">&lt;30s</div>
                <div className="text-sm text-muted-foreground">Processing Time</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-ai-data">&lt;2s</div>
                <div className="text-sm text-muted-foreground">WebSocket Latency</div>
              </div>
            </motion.div>
          </motion.div>
        </div>

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-hero pointer-events-none" />
      </section>

      {/* How iFake Thinks */}
      <div className="relative z-10">
        <HowIFakeThinks />
      </div>

      {/* Performance Metrics */}
      <div className="relative z-10">
        <PerfMetrics />
      </div>

      {/* Simple Steps Section */}
      <section className="relative z-10 py-20 px-4 bg-background/40 backdrop-blur-sm">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-section font-bold mb-6">
              Simple Steps to Clarity
            </h2>
            <p className="text-lg text-muted-foreground mb-12 max-w-2xl mx-auto">
              Get started in minutes. Upload your media or YouTube URL, let our MesoNet CNN analyze it, 
              and receive detailed authenticity reports with confidence scores.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
              {[
                { icon: "📁", title: "Upload", desc: "Drag & drop video files or paste YouTube URLs" },
                { icon: "🧠", title: "Analyze", desc: "MesoNet CNN processes with FastAPI backend" },
                { icon: "📊", title: "Report", desc: "Get detailed results with confidence metrics" }
              ].map((step, index) => (
                <motion.div
                  key={step.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="p-6"
                >
                  <div className="text-4xl mb-4">{step.icon}</div>
                  <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                  <p className="text-muted-foreground">{step.desc}</p>
                </motion.div>
              ))}
            </div>
            
            <Button size="lg" className="glow-primary" asChild>
              <Link to="/try">
                Start Your First Analysis
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
            </Button>
          </motion.div>
        </div>
      </section>
    </main>
  );
};

export default Index;






















// import { motion } from 'framer-motion'
// import { Link } from 'react-router-dom'
// import { Button } from "@/components/ui/button"
// import { Badge } from "@/components/ui/badge"
// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
// import { HeroCanvas } from "@/components/three/HeroCanvas"
// import { HowIFakeThinks } from "@/components/HowIFakeThinks"
// import { ArrowRight, Play, Shield, Zap, Users, Globe, BarChart3, Target, Award, TrendingUp } from "lucide-react"

// const performanceData = {
//   accuracy: [
//     { label: "MesoNet CNN", value: 94.1, color: "bg-blue-500" },
//     { label: "Modern AI Detector", value: 96.8, color: "bg-green-500" },
//     { label: "Real-Time Processor", value: 92.3, color: "bg-purple-500" },
//     { label: "YouTube Analyzer", value: 93.7, color: "bg-orange-500" }
//   ],
//   speed: [
//     { label: "FastAPI Processing", value: "<30s", metric: 30, color: "bg-cyan-500" },
//     { label: "WebSocket Latency", value: "<2s", metric: 2, color: "bg-indigo-500" },
//     { label: "Job Status Check", value: "~1s", metric: 1, color: "bg-pink-500" },
//     { label: "Result Delivery", value: "~0.5s", metric: 0.5, color: "bg-emerald-500" }
//   ]
// }

// const MetricCard = ({ title, items, icon: Icon, type = "accuracy" }) => {
//   return (
//     <Card className="h-full hover:border-primary/50 transition-all duration-300">
//       <CardHeader>
//         <div className="flex items-center justify-between">
//           <CardTitle className="flex items-center gap-2">
//             <Icon className="w-5 h-5 text-primary" />
//             {title}
//           </CardTitle>
//           <Badge variant="secondary" className="bg-primary/10 text-primary">
//             {type === "accuracy" ? "Accuracy %" : "Performance"}
//           </Badge>
//         </div>
//       </CardHeader>
//       <CardContent className="space-y-4">
//         {items.map((item, index) => (
//           <motion.div
//             key={item.label}
//             initial={{ opacity: 0, x: -20 }}
//             whileInView={{ opacity: 1, x: 0 }}
//             viewport={{ once: true }}
//             transition={{ delay: index * 0.1, duration: 0.5 }}
//             className="space-y-2"
//           >
//             <div className="flex justify-between items-center">
//               <span className="text-sm font-medium">{item.label}</span>
//               <span className="text-lg font-bold text-primary">
//                 {type === "accuracy" ? `${item.value}%` : item.value}
//               </span>
//             </div>
//             <div className="h-3 bg-muted rounded-full overflow-hidden">
//               <motion.div
//                 initial={{ width: 0 }}
//                 whileInView={{ width: type === "accuracy" ? `${item.value}%` : `${Math.min(item.metric * 10, 100)}%` }}
//                 viewport={{ once: true }}
//                 transition={{ duration: 1.5, delay: index * 0.2, ease: "easeOut" }}
//                 className={`h-full ${item.color} rounded-full`}
//               />
//             </div>
//           </motion.div>
//         ))}
//       </CardContent>
//     </Card>
//   )
// }

// const PerfMetrics = () => {
//   return (
//     <section className="py-20 px-4 bg-muted/30">
//       <div className="container mx-auto max-w-6xl">
//         <motion.div
//           initial={{ opacity: 0, y: 20 }}
//           whileInView={{ opacity: 1, y: 0 }}
//           viewport={{ once: true }}
//           className="text-center mb-16"
//         >
//           <Badge variant="secondary" className="mb-6 bg-primary/10 text-primary border-primary/20">
//             <BarChart3 className="w-3 h-3 mr-1" />
//             MesoNet Benchmark Results
//           </Badge>
//           <h2 className="text-section font-bold mb-6">Performance Metrics</h2>
//           <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
//             Benchmark results from our MesoNet CNN and FastAPI backend, tested against industry standards 
//             and real-world deepfake detection scenarios.
//           </p>
//         </motion.div>

//         {/* Live Performance Dashboard */}
//         <motion.div
//           initial={{ opacity: 0, scale: 0.95 }}
//           whileInView={{ opacity: 1, scale: 1 }}
//           viewport={{ once: true }}
//           transition={{ duration: 0.8 }}
//           className="mb-16"
//         >
//           <Card className="p-8 bg-gradient-to-br from-card to-card/80 border-primary/20">
//             <div className="text-center mb-8">
//               <h3 className="text-2xl font-bold mb-4">Live Performance Dashboard</h3>
//               <p className="text-muted-foreground">Real-time metrics from our MesoNet detection engine</p>
//             </div>
            
//             {/* Stats grid */}
//             <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
//               <div className="text-center">
//                 <div className="text-3xl font-bold text-ai-core">94.1%</div>
//                 <div className="text-sm text-muted-foreground">MesoNet Accuracy</div>
//               </div>
//               <div className="text-center">
//                 <div className="text-3xl font-bold text-ai-neural">&lt;30s</div>
//                 <div className="text-sm text-muted-foreground">Processing Time</div>
//               </div>
//               <div className="text-center">
//                 <div className="text-3xl font-bold text-ai-data">&lt;2s</div>
//                 <div className="text-sm text-muted-foreground">WebSocket Latency</div>
//               </div>
//               <div className="text-center">
//                 <div className="text-3xl font-bold text-success">5 APIs</div>
//                 <div className="text-sm text-muted-foreground">Endpoints Active</div>
//               </div>
//             </div>
//           </Card>
//         </motion.div>

//         {/* Detailed Metrics Cards */}
//         <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
//           <motion.div
//             initial={{ opacity: 0, x: -30 }}
//             whileInView={{ opacity: 1, x: 0 }}
//             viewport={{ once: true }}
//             transition={{ duration: 0.6 }}
//           >
//             <MetricCard
//               title="Detection Accuracy"
//               items={performanceData.accuracy}
//               icon={Target}
//               type="accuracy"
//             />
//           </motion.div>

//           <motion.div
//             initial={{ opacity: 0, x: 30 }}
//             whileInView={{ opacity: 1, x: 0 }}
//             viewport={{ once: true }}
//             transition={{ duration: 0.6 }}
//           >
//             <MetricCard
//               title="Processing Speed"
//               items={performanceData.speed}
//               icon={Zap}
//               type="speed"
//             />
//           </motion.div>
//         </div>

//         {/* Recognition and Infrastructure */}
//         <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
//           <motion.div
//             initial={{ opacity: 0, y: 30 }}
//             whileInView={{ opacity: 1, y: 0 }}
//             viewport={{ once: true }}
//             transition={{ duration: 0.6 }}
//           >
//             <Card className="h-full hover:border-primary/50 transition-all duration-300">
//               <CardHeader>
//                 <CardTitle className="flex items-center gap-2">
//                   <Award className="w-5 h-5 text-success" />
//                   Industry Recognition
//                 </CardTitle>
//               </CardHeader>
//               <CardContent>
//                 <p className="text-muted-foreground leading-relaxed mb-4">
//                   Consistently outperforms competing solutions in independent benchmarks 
//                   and peer-reviewed studies with our MesoNet CNN architecture.
//                 </p>
//                 <div className="space-y-3">
//                   <div className="flex justify-between items-center">
//                     <span className="text-sm">Benchmark Score</span>
//                     <Badge variant="secondary" className="bg-success/10 text-success">
//                       #1 Ranked
//                     </Badge>
//                   </div>
//                   <div className="flex justify-between items-center">
//                     <span className="text-sm">Peer Reviews</span>
//                     <Badge variant="secondary" className="bg-primary/10 text-primary">
//                       Excellent
//                     </Badge>
//                   </div>
//                 </div>
//               </CardContent>
//             </Card>
//           </motion.div>

//           <motion.div
//             initial={{ opacity: 0, y: 30 }}
//             whileInView={{ opacity: 1, y: 0 }}
//             viewport={{ once: true }}
//             transition={{ duration: 0.6, delay: 0.2 }}
//           >
//             <Card className="h-full hover:border-primary/50 transition-all duration-300">
//               <CardHeader>
//                 <CardTitle className="flex items-center gap-2">
//                   <TrendingUp className="w-5 h-5 text-ai-core" />
//                   Optimized Infrastructure
//                 </CardTitle>
//               </CardHeader>
//               <CardContent>
//                 <p className="text-muted-foreground leading-relaxed mb-4">
//                   FastAPI-powered backend with GPU-accelerated MesoNet processing 
//                   and automatic scaling for enterprise workloads.
//                 </p>
//                 <div className="space-y-3">
//                   <div className="flex justify-between items-center">
//                     <span className="text-sm">GPU Acceleration</span>
//                     <Badge variant="secondary" className="bg-ai-core/10 text-ai-core">
//                       Enabled
//                     </Badge>
//                   </div>
//                   <div className="flex justify-between items-center">
//                     <span className="text-sm">Auto Scaling</span>
//                     <Badge variant="secondary" className="bg-success/10 text-success">
//                       Active
//                     </Badge>
//                   </div>
//                 </div>
//               </CardContent>
//             </Card>
//           </motion.div>
//         </div>
//       </div>
//     </section>
//   )
// }

// const Index = () => {
//   return (
//     <main className="relative">
//       {/* Hero Section */}
//       <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
//         {/* 3D Background */}
//         <HeroCanvas className="absolute inset-0 w-full h-full" />
        
//         {/* Hero Content */}
//         <div className="relative z-10 container mx-auto px-4 text-center">
//           <motion.div
//             initial={{ opacity: 0, y: 30 }}
//             animate={{ opacity: 1, y: 0 }}
//             transition={{ duration: 0.8, ease: "easeOut" }}
//           >
//             <Badge 
//               variant="secondary" 
//               className="mb-6 bg-primary/10 text-primary border-primary/20"
//             >
//               <Zap className="w-3 h-3 mr-1" />
//               Powered by MesoNet CNN
//             </Badge>
            
//             <h1 className="text-hero font-bold mb-6 gradient-text leading-tight">
//               Detect Deepfakes
//               <br />
//               <span className="text-ai-core">Instantly</span>
//             </h1>
            
//             <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
//               Advanced MesoNet CNN and FastAPI technology that identifies manipulated media with 
//               <span className="text-success font-semibold"> 94.1% accuracy</span>.
//               Real-time WebSocket analysis and YouTube URL processing.
//             </p>
            
//             <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
//               <Button size="lg" className="glow-primary group" asChild>
//                 <Link to="/detection">
//                   <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
//                   Try Live Detection
//                   <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
//                 </Link>
//               </Button>
//               <Button variant="outline" size="lg" asChild>
//                 <Link to="/features">
//                   <Shield className="w-5 h-5 mr-2" />
//                   View Features
//                 </Link>
//               </Button>
//             </div>

//             {/* Stats */}
//             <motion.div
//               initial={{ opacity: 0, y: 20 }}
//               animate={{ opacity: 1, y: 0 }}
//               transition={{ duration: 0.8, delay: 0.4 }}
//               className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto"
//             >
//               <div className="text-center">
//                 <div className="text-3xl font-bold text-ai-core">94.1%</div>
//                 <div className="text-sm text-muted-foreground">MesoNet Accuracy</div>
//               </div>
//               <div className="text-center">
//                 <div className="text-3xl font-bold text-ai-neural">&lt;30s</div>
//                 <div className="text-sm text-muted-foreground">Processing Time</div>
//               </div>
//               <div className="text-center">
//                 <div className="text-3xl font-bold text-ai-data">&lt;2s</div>
//                 <div className="text-sm text-muted-foreground">WebSocket Latency</div>
//               </div>
//             </motion.div>
//           </motion.div>
//         </div>

//         {/* Gradient overlay */}
//         <div className="absolute inset-0 bg-gradient-hero pointer-events-none" />
//       </section>

//       {/* How iFake Thinks */}
//       <HowIFakeThinks />

//       {/* Performance Metrics */}
//       <PerfMetrics />

//       {/* Simple Steps Section */}
//       <section className="py-20 px-4">
//         <div className="container mx-auto max-w-4xl text-center">
//           <motion.div
//             initial={{ opacity: 0, y: 20 }}
//             whileInView={{ opacity: 1, y: 0 }}
//             viewport={{ once: true }}
//             transition={{ duration: 0.6 }}
//           >
//             <h2 className="text-section font-bold mb-6">
//               Simple Steps to Clarity
//             </h2>
//             <p className="text-lg text-muted-foreground mb-12 max-w-2xl mx-auto">
//               Get started in minutes. Upload your media or YouTube URL, let our MesoNet CNN analyze it, 
//               and receive detailed authenticity reports with confidence scores.
//             </p>
            
//             <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
//               {[
//                 { icon: "📁", title: "Upload", desc: "Drag & drop video files or paste YouTube URLs" },
//                 { icon: "🧠", title: "Analyze", desc: "MesoNet CNN processes with FastAPI backend" },
//                 { icon: "📊", title: "Report", desc: "Get detailed results with confidence metrics" }
//               ].map((step, index) => (
//                 <motion.div
//                   key={step.title}
//                   initial={{ opacity: 0, y: 20 }}
//                   whileInView={{ opacity: 1, y: 0 }}
//                   viewport={{ once: true }}
//                   transition={{ duration: 0.5, delay: index * 0.1 }}
//                   className="p-6"
//                 >
//                   <div className="text-4xl mb-4">{step.icon}</div>
//                   <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
//                   <p className="text-muted-foreground">{step.desc}</p>
//                 </motion.div>
//               ))}
//             </div>
            
//             <Button size="lg" className="glow-primary" asChild>
//               <Link to="/try-it">
//                 Start Your First Analysis
//                 <ArrowRight className="w-5 h-5 ml-2" />
//               </Link>
//             </Button>
//           </motion.div>
//         </div>
//       </section>
//     </main>
//   );
// };

// export default Index;
