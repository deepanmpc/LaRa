import React, { useEffect, useRef, useState } from 'react';

/**
 * CustomCursor.jsx
 *
 * Two-layer system:
 *  1. Inner dot   — snaps immediately to pointer (crisp centre)
 *  2. Outer ring  — follows with a gentle lerp (trailing aura)
 *
 * Expands on hoverable elements (a, button, [data-cursor-grow]).
 * Hides the native cursor on the landing page wrapper.
 */
const CustomCursor = () => {
  const dotRef = useRef(null);
  const ringRef = useRef(null);
  const mouse = useRef({ x: -100, y: -100 });
  const ring = useRef({ x: -100, y: -100 });
  const growing = useRef(false);
  const raf = useRef(null);

  useEffect(() => {
    const onMove = (e) => {
      mouse.current = { x: e.clientX, y: e.clientY };
    };

    const onEnter = (e) => {
      const el = e.target;
      if (el.matches('button, a, [data-cursor-grow]')) growing.current = true;
    };
    const onLeave = (e) => {
      const el = e.target;
      if (el.matches('button, a, [data-cursor-grow]')) growing.current = false;
    };

    window.addEventListener('mousemove', onMove);
    document.addEventListener('mouseenter', onEnter, true);
    document.addEventListener('mouseleave', onLeave, true);

    const loop = () => {
      // Inner dot: snap
      if (dotRef.current) {
        dotRef.current.style.transform = `translate(${mouse.current.x - 4}px, ${mouse.current.y - 4}px)`;
      }

      // Outer ring: lerp
      ring.current.x += (mouse.current.x - ring.current.x) * 0.12;
      ring.current.y += (mouse.current.y - ring.current.y) * 0.12;
      if (ringRef.current) {
        const size = growing.current ? 42 : 26;
        const offset = size / 2;
        ringRef.current.style.width = `${size}px`;
        ringRef.current.style.height = `${size}px`;
        ringRef.current.style.transform = `translate(${ring.current.x - offset}px, ${ring.current.y - offset}px)`;
        ringRef.current.style.opacity = growing.current ? '0.6' : '0.35';
      }

      raf.current = requestAnimationFrame(loop);
    };
    loop();

    return () => {
      window.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseenter', onEnter, true);
      document.removeEventListener('mouseleave', onLeave, true);
      cancelAnimationFrame(raf.current);
    };
  }, []);

  return (
    <>
      {/* Inner dot */}
      <div
        ref={dotRef}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: 8,
          height: 8,
          borderRadius: '50%',
          backgroundColor: '#1a1a1a',
          zIndex: 99999,
          pointerEvents: 'none',
          willChange: 'transform'
        }}
      />
      {/* Outer ring */}
      <div
        ref={ringRef}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: 26,
          height: 26,
          borderRadius: '50%',
          border: '1.5px solid rgba(74, 144, 226, 0.7)',
          zIndex: 99998,
          pointerEvents: 'none',
          willChange: 'transform, width, height',
          transition: 'width 0.25s ease, height 0.25s ease, opacity 0.25s ease',
          backdropFilter: 'blur(0px)'
        }}
      />
    </>
  );
};

export default CustomCursor;
