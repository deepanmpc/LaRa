import { motion } from 'framer-motion';
import { Scan, Cpu, Sparkles, TrendingUp } from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: Scan,
    title: 'Sensing & Input',
    description: 'LARA captures facial expressions, movements, and engagement levels through advanced webcam technology.',
  },
  {
    number: '02',
    icon: Cpu,
    title: 'AI Processing',
    description: 'Our emotion classifier and attention detection algorithms analyze data in real-time.',
  },
  {
    number: '03',
    icon: Sparkles,
    title: 'Adaptive Response',
    description: 'The therapy engine adjusts activities and modifies difficulty based on emotional feedback.',
  },
  {
    number: '04',
    icon: TrendingUp,
    title: 'Progress Tracking',
    description: 'All interactions are logged to provide comprehensive progress reports for caregivers.',
  },
];

const HowItWorksSection = () => {
  return (
    <section id="how-it-works" className="relative py-24 bg-muted/30">
      <div className="container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-primary font-medium tracking-wider text-sm">HOW IT WORKS</span>
          <h2 className="font-display text-3xl md:text-4xl font-bold mt-3 mb-4 text-foreground">
            Smart Therapy, Step by Step
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            LARA uses a continuous feedback loop to provide personalized, adaptive therapy sessions.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="text-center"
            >
              <div className="relative inline-block mb-6">
                <div className="w-16 h-16 rounded-2xl bg-card shadow-md flex items-center justify-center border border-border">
                  <step.icon className="w-7 h-7 text-primary" />
                </div>
                <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-primary text-primary-foreground text-xs font-bold flex items-center justify-center">
                  {step.number}
                </span>
              </div>
              <h3 className="font-display text-lg font-semibold mb-2 text-foreground">
                {step.title}
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
