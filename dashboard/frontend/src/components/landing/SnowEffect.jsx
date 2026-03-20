import React, { useEffect, useRef } from 'react';

/**
 * SnowEffect.jsx — Lightweight canvas-based snowfall
 * Uses requestAnimationFrame directly for 60fps performance.
 * Particles are very small and semi-transparent to stay subtle.
 */
const SnowEffect = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let raf;
    let particles = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // Spawn particles
    const COUNT = 180;
    const spawn = () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height - canvas.height,
      r: Math.random() * 2.8 + 1.0,
      speed: Math.random() * 0.7 + 0.35,
      drift: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.37 + 0.18
    });

    for (let i = 0; i < COUNT; i++) {
      particles.push({ ...spawn(), y: Math.random() * canvas.height });
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (const p of particles) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(140, 180, 215, ${p.opacity})`;
        ctx.fill();

        p.y += p.speed;
        p.x += p.drift;

        if (p.y > canvas.height + 4) {
          Object.assign(p, spawn(), { y: -4 });
        }
        if (p.x > canvas.width + 4) p.x = -4;
        if (p.x < -4) p.x = canvas.width + 4;
      }

      raf = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        zIndex: 1,
        pointerEvents: 'none'
      }}
    />
  );
};

export default SnowEffect;
