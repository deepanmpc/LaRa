import { motion } from 'framer-motion';
import { Heart, Users, BookOpen, Lightbulb } from 'lucide-react';

const conditions = [
  {
    icon: Heart,
    title: 'Down Syndrome',
    description: 'Specialized cognitive and motor skill development activities tailored to support children in reaching their full potential.',
    color: 'bg-rose-50 text-rose-500',
  },
  {
    icon: Users,
    title: 'Autism Spectrum',
    description: 'Structured, predictable interactions that help children develop social skills, communication, and emotional regulation.',
    color: 'bg-sky-50 text-sky-500',
  },
  {
    icon: BookOpen,
    title: 'Learning Disabilities',
    description: 'Adaptive educational games designed to strengthen reading, writing, and mathematical abilities at each child\'s pace.',
    color: 'bg-violet-50 text-violet-500',
  },
  {
    icon: Lightbulb,
    title: 'Intellectual Disorders',
    description: 'Patient, repetitive, and engaging activities that support cognitive development and help build essential life skills.',
    color: 'bg-amber-50 text-amber-500',
  },
];

const WhoWeHelpSection = () => {
  return (
    <section id="who-we-help" className="relative py-24">
      <div className="container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-primary font-medium tracking-wider text-sm">WHO WE HELP</span>
          <h2 className="font-display text-3xl md:text-4xl font-bold mt-3 mb-4 text-foreground">
            Supporting Children with Diverse Needs
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            LARA provides specialized support for children across developmental and learning conditions.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {conditions.map((condition, index) => (
            <motion.div
              key={condition.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="soft-card p-8 flex gap-5"
            >
              <div className={`w-12 h-12 rounded-xl ${condition.color} flex items-center justify-center flex-shrink-0`}>
                <condition.icon className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-display text-lg font-semibold mb-2 text-foreground">
                  {condition.title}
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {condition.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default WhoWeHelpSection;
