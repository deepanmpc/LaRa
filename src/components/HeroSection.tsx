import { motion } from 'framer-motion';
import Robot3D from './Robot3D';

const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20">
      <div className="container mx-auto px-6 py-20">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center lg:text-left"
          >
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="inline-block mb-6"
            >
              <span className="px-4 py-2 rounded-full text-xs font-medium tracking-wider text-primary bg-primary/10 border border-primary/20">
                AI-POWERED THERAPY
              </span>
            </motion.div>

            <h1 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6 text-foreground">
              Empowering Every{' '}
              <span className="gradient-text">Ability</span>
              {' '}with Care & Innovation
            </h1>

            <p className="text-muted-foreground text-lg mb-8 max-w-xl mx-auto lg:mx-0 leading-relaxed">
              Low-cost adaptive robotic-AI therapy system for children with Down Syndrome, 
              Learning Disabilities, Intellectual Disorders and Autism.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-8 py-4 bg-primary rounded-full text-primary-foreground font-semibold shadow-lg hover:shadow-xl transition-shadow"
              >
                Learn More
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-8 py-4 rounded-full font-semibold border border-border text-foreground hover:bg-muted transition-colors"
              >
                Watch Demo
              </motion.button>
            </div>

            <div className="flex flex-wrap gap-8 mt-12 justify-center lg:justify-start">
              {[
                { value: '24/7', label: 'Monitoring' },
                { value: 'AI', label: 'Powered' },
                { value: 'Low', label: 'Cost' },
              ].map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
                  className="text-center"
                >
                  <span className="text-2xl font-bold text-primary">{stat.value}</span>
                  <span className="text-muted-foreground ml-2">{stat.label}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="relative flex justify-center"
          >
            <Robot3D />
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
