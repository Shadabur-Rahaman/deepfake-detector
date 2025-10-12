import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Eye, Brain, Shield, Zap, CheckCircle } from "lucide-react"

const steps = [
  {
    icon: Eye,
    title: "Visual Analysis",
    description: "Advanced computer vision examines pixel-level inconsistencies and temporal artifacts",
    delay: 0.1
  },
  {
    icon: Brain,
    title: "Neural Processing", 
    description: "Deep learning models trained on millions of authentic and manipulated samples",
    delay: 0.2
  },
  {
    icon: Zap,
    title: "Pattern Recognition",
    description: "Identifies subtle manipulation patterns invisible to the human eye",
    delay: 0.3
  },
  {
    icon: Shield,
    title: "Confidence Scoring",
    description: "Multi-layered validation provides precise authenticity confidence levels",
    delay: 0.4
  },
  {
    icon: CheckCircle,
    title: "Verdict Delivery",
    description: "Clear, actionable results with detailed explanation of findings",
    delay: 0.5
  }
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      duration: 0.6
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.4, 0, 0.2, 1] as any
    }
  }
}

export function HowIFakeThinks() {
  return (
    <section className="py-20 px-4">
      <div className="container mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-section font-bold mb-6 gradient-text">
            How iFake Thinks
          </h2>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Our AI detection pipeline combines multiple advanced techniques to deliver 
            unprecedented accuracy in identifying manipulated content.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              variants={itemVariants}
              className="group"
            >
              <Card className="h-full border-border/50 bg-card/50 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 hover:shadow-glow">
                <CardHeader className="text-center pb-4">
                  <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-gradient-primary flex items-center justify-center group-hover:glow-primary transition-all duration-300">
                    <step.icon className="w-8 h-8 text-primary-foreground" />
                  </div>
                  <CardTitle className="text-xl mb-2">{step.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-center leading-relaxed">
                    {step.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="text-center mt-16"
        >
          <div className="inline-flex items-center space-x-2 text-sm text-muted-foreground bg-muted/50 px-4 py-2 rounded-full">
            <Zap className="w-4 h-4 text-ai-core" />
            <span>Processing time: &lt;2 seconds per analysis</span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}