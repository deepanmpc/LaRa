import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

const benefits = [
  'Affordable therapy accessible to all families',
  'Works offline - no internet required',
  'Reduces dependency on full-time therapists',
  'Personalized learning at each child\'s pace',
  'Real-time emotional support and adaptation',
  'Comprehensive progress tracking and reports',
];

const AboutSection = () => {
  return (
    <section id="about" className="relative py-24 bg-muted/30">
      <div className="container mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <span className="text-primary font-medium tracking-wider text-sm">ABOUT LARA</span>
            <h2 className="font-display text-3xl md:text-4xl font-bold mt-3 mb-6 text-foreground">
              Making Therapy Accessible to Every Child
            </h2>
            <p className="text-muted-foreground mb-6 leading-relaxed">
              LARA (Low-cost Adaptive Robotic-AI Therapy System) is designed to provide 
              affordable, AI-powered therapy assistance for children with Down Syndrome, 
              Autism, Learning Disabilities, and Intellectual Disorders.
            </p>
            <p className="text-muted-foreground mb-8 leading-relaxed">
              Our mission is to ensure that every child, regardless of their family's 
              financial situation or location, has access to quality therapeutic care.
            </p>

            <div className="grid sm:grid-cols-2 gap-3">
              {benefits.map((benefit, index) => (
                <motion.div
                  key={benefit}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: index * 0.05 }}
                  className="flex items-center gap-3"
                >
                  <div className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Check className="w-3 h-3 text-primary" />
                  </div>
                  <span className="text-foreground/80 text-sm">{benefit}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="soft-card p-8 md:p-10"
          >
            <h3 className="font-display text-xl font-bold mb-4 text-foreground">
              LARA Research Group
            </h3>
            <p className="text-muted-foreground mb-6 leading-relaxed">
              Innovation at KL University for Therapeutic Robotics. Our dedicated research team 
              develops cutting-edge AI-powered robotic solutions to help children with special 
              needs through therapeutic intervention.
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-muted/50 rounded-xl text-center">
                <div className="text-2xl font-bold text-primary mb-1">AI</div>
                <div className="text-muted-foreground text-xs">Powered Intelligence</div>
              </div>
              <div className="p-4 bg-muted/50 rounded-xl text-center">
                <div className="text-2xl font-bold text-primary mb-1">24/7</div>
                <div className="text-muted-foreground text-xs">Continuous Support</div>
              </div>
              <div className="p-4 bg-muted/50 rounded-xl text-center">
                <div className="text-2xl font-bold text-primary mb-1">100%</div>
                <div className="text-muted-foreground text-xs">Personalized Care</div>
              </div>
              <div className="p-4 bg-muted/50 rounded-xl text-center">
                <div className="text-2xl font-bold text-primary mb-1">Low</div>
                <div className="text-muted-foreground text-xs">Cost Solution</div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;
