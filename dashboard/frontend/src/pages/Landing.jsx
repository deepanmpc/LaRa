import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import Intro from '../components/landing/Intro';
import SnowEffect from '../components/landing/SnowEffect';
import CustomCursor from '../components/landing/CustomCursor';

export default function Landing() {
  const [introComplete, setIntroComplete] = useState(false);
  const navigate = useNavigate();

  return (
    /* Hide native cursor so our custom one shows */
    <div style={{ cursor: 'none', width: '100vw', height: '100vh', overflow: 'hidden', position: 'fixed', inset: 0 }}>

      {/* Custom cursor — always on top */}
      <CustomCursor />

      {/* Intro sequence */}
      <Intro onComplete={() => setIntroComplete(true)} />

      {/* Main light-theme page */}
      <motion.div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(160deg, #ffffff 0%, #f0f6ff 55%, #e8f2ff 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 0
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: introComplete ? 1 : 0 }}
        transition={{ duration: 0.9, ease: 'easeOut' }}
      >
        {/* Snow effect — subtle depth layer */}
        <SnowEffect />

        {/* Very faint top-left radial blur accent */}
        <div style={{
          position: 'absolute',
          top: '-10%',
          left: '-10%',
          width: '55vw',
          height: '55vw',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(74,144,226,0.06) 0%, transparent 70%)',
          pointerEvents: 'none',
          zIndex: 2
        }} />

        {/* Content */}
        <motion.div
          style={{
            position: 'relative',
            zIndex: 10,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            padding: '0 24px'
          }}
          initial={{ opacity: 0, y: 22 }}
          animate={introComplete ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 }}
          transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1], delay: 0.15 }}
        >
          {/* Title */}
          <h1
            style={{
              fontFamily: '"Goldman", sans-serif',
              fontWeight: 700,
              fontSize: 'clamp(3.2rem, 9vw, 7rem)',
              letterSpacing: '0.04em',
              margin: '0 0 12px 0',
              background: 'linear-gradient(135deg, #0a0a0a 30%, #1a3a6b 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              lineHeight: 1.05
            }}
          >
            LaRa
          </h1>

          {/* Description */}
          <p
            style={{
              fontFamily: '"Inter", system-ui, sans-serif',
              fontWeight: 400,
              fontSize: 'clamp(0.95rem, 2.2vw, 1.15rem)',
              color: '#6B7280',
              maxWidth: '420px',
              lineHeight: 1.65,
              margin: '0 0 28px 0'
            }}
          >
            A learning companion powered by hidden clinical intelligence.
          </p>

          {/* CTA Button */}
          <motion.button
            whileHover={{ scale: 1.05, boxShadow: '0 6px 30px rgba(0,0,0,0.18)' }}
            whileTap={{ scale: 0.97 }}
            transition={{ type: 'spring', stiffness: 400, damping: 22 }}
            onClick={() => navigate('/login')}
            style={{
              fontFamily: '"Inter", sans-serif',
              fontWeight: 600,
              fontSize: '0.98rem',
              letterSpacing: '0.04em',
              color: '#ffffff',
              backgroundColor: '#0a0a0a',
              border: 'none',
              borderRadius: '9999px',
              padding: '14px 44px',
              cursor: 'none',
              boxShadow: '0 2px 12px rgba(0,0,0,0.12)',
              transition: 'background-color 0.2s ease'
            }}
          >
            Get Started
          </motion.button>

          {/* Subtle brand tag */}
          <motion.span
            initial={{ opacity: 0 }}
            animate={introComplete ? { opacity: 1 } : {}}
            transition={{ delay: 1.2, duration: 0.8 }}
            style={{
              fontFamily: '"Inter", sans-serif',
              fontSize: '0.65rem',
              letterSpacing: '0.2em',
              color: '#b0bec5',
              textTransform: 'uppercase',
              marginTop: '32px'
            }}
          >
            Clinical AI · Learning Intelligence
          </motion.span>
        </motion.div>
      </motion.div>
    </div>
  );
}
