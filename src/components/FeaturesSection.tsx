import { motion } from 'framer-motion';
import { Eye, Heart, Brain, Activity, Gamepad2, BarChart3 } from 'lucide-react';

const features = [
  {
    icon: Eye,
    title: 'Robotic Eyes Monitoring',
    description: 'Continuous monitoring using advanced computer vision to track child behavior and engagement in real-time.',
  },
  {
    icon: Heart,
    title: 'Emotion Detection',
    description: 'AI-powered facial expression analysis to understand emotions and adapt therapy sessions accordingly.',
  },
  {
    icon: Brain,
    title: 'Adaptive Learning',
    description: 'Personalized teaching at each child\'s own pace, adjusting difficulty based on progress and mood.',
  },
  {
    icon: Activity,
    title: 'Health Monitoring',
    description: 'Tracks behavioral patterns and health indicators to provide insights to caregivers and therapists.',
  },
  {
    icon: Gamepad2,
    title: 'Gamified Therapy',
    description: 'Interactive games for cognitive development, speech training, and motor skill improvement.',
  },
  {
    icon: BarChart3,
    title: 'Progress Dashboard',
    description: 'Comprehensive analytics and reports for parents and therapists to track development milestones.',
  },
];

const FeaturesSection = () => {
  return (
    <section id="features" className="relative py-24">
      <div className="container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-primary font-medium tracking-wider text-sm">FEATURES</span>
          <h2 className="font-display text-3xl md:text-4xl font-bold mt-3 mb-4 text-foreground">
            Comprehensive Care Through Technology
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            LARA combines cutting-edge AI with compassionate care for holistic therapy support.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="soft-card p-8 hover:border-primary/30 transition-all duration-300 group"
            >
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-5 group-hover:bg-primary/20 transition-colors">
                <feature.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-display text-lg font-semibold mb-2 text-foreground">
                {feature.title}
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
