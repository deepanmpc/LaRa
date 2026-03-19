import React, { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';

/**
 * Intro.jsx — Dark → Light cinematic boot sequence
 *
 * Phases:
 *  'in'   — black bg, white LaRa fades in + scales up
 *  'flip' — bg transitions black → white, text white → black
 *  'out'  — overlay fades away, revealing light landing
 *  'done' — unmounts
 *
 * hasRun ref: guards against React StrictMode's double-effect invocation
 * so the intro never plays twice.
 */
const Intro = ({ onComplete }) => {
  const [phase, setPhase] = useState('in');
  const hasRun = useRef(false);
  const onCompleteRef = useRef(onComplete);

  useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

  useEffect(() => {
    // StrictMode: first (fake) mount → sets timers → cleanup clears + resets flag
    //             second (real) mount → hasRun is false again → timers start for real
    if (hasRun.current) return;
    hasRun.current = true;

    const t1 = setTimeout(() => setPhase('flip'), 1600);
    const t2 = setTimeout(() => setPhase('out'),  2600);
    const t3 = setTimeout(() => {
      setPhase('done');
      onCompleteRef.current?.();
    }, 3300);

    return () => {
      clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
      hasRun.current = false; // allow the real second mount to proceed
    };
  }, []); // intentionally empty — run exactly once per real mount


  if (phase === 'done') return null;

  const bgColor   = (phase === 'flip' || phase === 'out') ? '#ffffff' : '#000000';
  const textColor = (phase === 'flip' || phase === 'out') ? '#000000' : '#ffffff';
  const textGlow  = phase === 'in'
    ? 'drop-shadow(0 0 24px rgba(255,255,255,0.45))'
    : 'none';

  return (
    <motion.div
      style={{
        position: 'fixed',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        pointerEvents: 'none',
        backgroundColor: bgColor,
        transition: 'background-color 0.9s ease'
      }}
      animate={{ opacity: phase === 'out' ? 0 : 1 }}
      transition={{ duration: 0.7, ease: 'easeInOut' }}
    >
      <motion.h1
        style={{
          fontFamily: '"Goldman", sans-serif',
          fontWeight: 700,
          fontSize: 'clamp(4.5rem, 13vw, 9rem)',
          letterSpacing: '0.04em',
          margin: 0,
          color: textColor,
          filter: textGlow,
          transition: 'color 0.9s ease, filter 0.9s ease',
          willChange: 'transform, opacity'
        }}
        initial={{ opacity: 0, scale: 0.84 }}
        animate={{
          opacity: phase === 'out' ? 0 : 1,
          scale:   phase === 'out' ? 0.92 : 1
        }}
        transition={{
          duration: phase === 'in' ? 1.2 : 0.6,
          ease: [0.16, 1, 0.3, 1]
        }}
      >
        LaRa
      </motion.h1>
    </motion.div>
  );
};

export default Intro;
