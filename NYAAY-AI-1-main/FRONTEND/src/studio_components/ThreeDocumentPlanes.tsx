import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { BARE_ACTS_CATALOG } from '../data/bareActsData';
import { BareAct } from '../types';
import { Layers, Eye, ShieldCheck, Box, Sparkles, Check } from 'lucide-react';

interface ThreeDocumentPlanesProps {
  activeActId?: string;
  isConverging?: boolean;
  onSelectAct?: (actId: string) => void;
  onInspectAct?: (act: BareAct) => void;
  className?: string;
}

// Helper to generate soft radial contact shadow texture for paper planes
function createContactShadowTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 128;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    // Soft elliptical drop shadow
    const grad = ctx.createRadialGradient(128, 64, 4, 128, 64, 115);
    grad.addColorStop(0, 'rgba(18, 24, 32, 0.40)');
    grad.addColorStop(0.35, 'rgba(18, 24, 32, 0.22)');
    grad.addColorStop(0.70, 'rgba(26, 24, 20, 0.08)');
    grad.addColorStop(1, 'rgba(26, 24, 20, 0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 256, 128);
  }
  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}

// Procedural Canvas Texture Generator for realistic documentary legal paper planes
function createDocumentTexture(act: BareAct, isActive: boolean): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 724; // A4 aspect ratio
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    return new THREE.CanvasTexture(canvas);
  }

  // Directional lighting gradient on card surface from upper-left (subtle 3-5% paper catch)
  const surfaceGrad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  if (isActive) {
    surfaceGrad.addColorStop(0, '#FFFFFF');
    surfaceGrad.addColorStop(0.65, '#FDFCF9');
    surfaceGrad.addColorStop(1, '#F7F1E8');
  } else {
    surfaceGrad.addColorStop(0, '#FFFFFF');
    surfaceGrad.addColorStop(0.40, '#FAF7F2');
    surfaceGrad.addColorStop(1, '#EEE6D8');
  }
  ctx.fillStyle = surfaceGrad;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Outer border & ruled lines
  ctx.strokeStyle = isActive ? '#C84B31' : '#D5CEC2';
  ctx.lineWidth = isActive ? 10 : 4;
  ctx.strokeRect(16, 16, canvas.width - 32, canvas.height - 32);

  // Inner margin header
  ctx.fillStyle = isActive ? '#C84B31' : '#121820';
  ctx.fillRect(24, 24, canvas.width - 48, 48);

  // Header Text
  ctx.fillStyle = '#FAF7F2';
  ctx.font = 'bold 20px monospace';
  ctx.fillText(`INDIA STATUTE // ${act.actCode}`, 40, 56);

  // Title in editorial serif
  ctx.fillStyle = '#121820';
  ctx.font = 'bold 30px serif';
  
  // Word wrap title
  const words = act.title.split(' ');
  let line = '';
  let y = 120;
  for (let i = 0; i < words.length; i++) {
    const testLine = line + words[i] + ' ';
    const metrics = ctx.measureText(testLine);
    if (metrics.width > 420 && i > 0) {
      ctx.fillText(line, 40, y);
      line = words[i] + ' ';
      y += 38;
      if (y > 220) break;
    } else {
      line = testLine;
    }
  }
  ctx.fillText(line, 40, y);

  // Metadata badge
  ctx.fillStyle = '#556377';
  ctx.font = '16px monospace';
  ctx.fillText(`YEAR: ${act.year} • SECTIONS: ${act.sectionCount}`, 40, y + 40);

  // Ruled legal paper lines
  ctx.strokeStyle = '#F2EFE9';
  ctx.lineWidth = 2;
  for (let ly = y + 70; ly < canvas.height - 100; ly += 28) {
    ctx.beginPath();
    ctx.moveTo(40, ly);
    ctx.lineTo(canvas.width - 40, ly);
    ctx.stroke();
  }

  // Stamp badge at bottom
  if (isActive) {
    ctx.save();
    ctx.translate(canvas.width - 140, canvas.height - 70);
    ctx.rotate(-0.1);
    ctx.strokeStyle = '#C84B31';
    ctx.lineWidth = 4;
    ctx.strokeRect(-80, -26, 160, 52);
    ctx.fillStyle = '#C84B31';
    ctx.font = 'bold 18px monospace';
    ctx.fillText('RRF GROUNDED', -70, 6);
    ctx.restore();
  } else {
    ctx.fillStyle = '#667085';
    ctx.font = 'bold 16px monospace';
    ctx.fillText('CLICK TO INSPECT DOSSIER →', 40, canvas.height - 50);
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.anisotropy = 4;
  return texture;
}

const ThreeDocumentPlanesComponent: React.FC<ThreeDocumentPlanesProps> = ({
  activeActId = 'rti-2005',
  isConverging = true,
  onSelectAct,
  onInspectAct,
  className = ''
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [hoveredAct, setHoveredAct] = useState<BareAct | null>(null);
  const [selectedActState, setSelectedActState] = useState<string>(activeActId);
  const [isWebGlSupported, setIsWebGlSupported] = useState<boolean>(true);
  const [force2DMode, setForce2DMode] = useState<boolean>(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(false);
  const [interactionHint, setInteractionHint] = useState<string>('Hover over or click any document to open its full legislative section inspector');

  useEffect(() => {
    setSelectedActState(activeActId);
  }, [activeActId]);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  useEffect(() => {
    if (!mountRef.current || prefersReducedMotion || force2DMode) return;

    const container = mountRef.current;
    const width = container.clientWidth || 600;
    const height = container.clientHeight || 400;

    // Check WebGL
    try {
      const testCanvas = document.createElement('canvas');
      const gl = testCanvas.getContext('webgl') || testCanvas.getContext('experimental-webgl');
      if (!gl) {
        setIsWebGlSupported(false);
        return;
      }
    } catch {
      setIsWebGlSupported(false);
      return;
    }

    // Scene with atmospheric depth fog
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0xF5EFE6, 0.038);

    // Camera
    const camera = new THREE.PerspectiveCamera(44, width / height, 0.1, 100);
    camera.position.set(0, 3.2, 8.8);
    camera.lookAt(0, 0.3, 0);

    // Renderer (transparent alpha to blend with paper case-file dotted texture)
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Ground Plane — subtle tabletop surface gradient with fine table edge guideline
    const groundCanvas = document.createElement('canvas');
    groundCanvas.width = 512;
    groundCanvas.height = 512;
    const gCtx = groundCanvas.getContext('2d');
    if (gCtx) {
      const gGrad = gCtx.createLinearGradient(0, 0, 0, 512);
      gGrad.addColorStop(0, 'rgba(245, 239, 230, 0.15)');
      gGrad.addColorStop(0.48, 'rgba(240, 233, 222, 0.55)');
      gGrad.addColorStop(0.50, 'rgba(213, 206, 194, 0.40)'); // Table edge line
      gGrad.addColorStop(0.52, 'rgba(235, 227, 215, 0.70)');
      gGrad.addColorStop(1, 'rgba(228, 219, 206, 0.85)');
      gCtx.fillStyle = gGrad;
      gCtx.fillRect(0, 0, 512, 512);
    }
    const groundTexture = new THREE.CanvasTexture(groundCanvas);
    const groundMat = new THREE.MeshBasicMaterial({
      map: groundTexture,
      transparent: true,
      opacity: 0.85
    });
    const groundMesh = new THREE.Mesh(new THREE.PlaneGeometry(32, 22), groundMat);
    groundMesh.rotation.x = -Math.PI / 2;
    groundMesh.position.set(0, -0.92, 0);
    groundMesh.raycast = () => {}; // Never swallow click raycasts
    scene.add(groundMesh);

    // Lighting (directional from upper-left matching UI shadow conventions)
    const ambientLight = new THREE.AmbientLight(0xFFFDF8, 1.6);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xFFF6EC, 1.8);
    dirLight.position.set(-5, 10, 7);
    scene.add(dirLight);

    const accentLight = new THREE.PointLight(0xC84B31, 1.8, 10);
    accentLight.position.set(0, 1.8, 2.5);
    scene.add(accentLight);

    // Shared contact shadow texture & geometry
    const shadowTexture = createContactShadowTexture();
    const shadowGeo = new THREE.PlaneGeometry(1.6, 0.8);

    // Group for planes
    const planeGroup = new THREE.Group();
    scene.add(planeGroup);

    // Document Plane Geometry (approx 1.25 x 1.77)
    const planeGeo = new THREE.PlaneGeometry(1.25, 1.77, 1, 1);
    const edgesGeo = new THREE.EdgesGeometry(planeGeo);

    // Select acts from catalog to form the arc
    const acts = BARE_ACTS_CATALOG.slice(0, 18);
    const total = acts.length;

    const planes: {
      mesh: THREE.Mesh;
      border: THREE.LineSegments;
      shadowMesh: THREE.Mesh;
      act: BareAct;
      targetPos: THREE.Vector3;
      targetRot: THREE.Euler;
      originalPos: THREE.Vector3;
      originalRot: THREE.Euler;
      texture: THREE.CanvasTexture;
      activeTexture: THREE.CanvasTexture;
      mat: THREE.MeshStandardMaterial;
    }[] = [];

    acts.forEach((act, idx) => {
      const isActive = act.id === selectedActState;
      const normalTex = createDocumentTexture(act, false);
      const activeTex = createDocumentTexture(act, true);

      const mat = new THREE.MeshStandardMaterial({
        map: isActive ? activeTex : normalTex,
        roughness: 0.72,
        metalness: 0.04,
        transparent: true,
        opacity: isActive ? 1.0 : 0.85,
        side: THREE.DoubleSide
      });

      const mesh = new THREE.Mesh(planeGeo, mat);

      const borderMat = new THREE.LineBasicMaterial({
        color: isActive ? 0xC84B31 : 0x8896A6,
        linewidth: isActive ? 3 : 1,
        transparent: true,
        opacity: isActive ? 1 : 0.4
      });
      const border = new THREE.LineSegments(edgesGeo, borderMat);
      border.raycast = () => {}; // Prevent line from swallowing raycast
      mesh.add(border);

      // Contact shadow mesh for this card on the tabletop
      const shadowMat = new THREE.MeshBasicMaterial({
        map: shadowTexture,
        transparent: true,
        opacity: isActive ? 0.22 : 0.14,
        depthWrite: false
      });
      const shadowMesh = new THREE.Mesh(shadowGeo, shadowMat);
      shadowMesh.rotation.x = -Math.PI / 2;
      shadowMesh.position.y = -0.90;
      shadowMesh.raycast = () => {};
      scene.add(shadowMesh);

      // Distribute in a balanced fan arc
      const angle = ((idx - (total - 1) / 2) / total) * (Math.PI * 0.9);
      const radius = 4.6;
      const x = Math.sin(angle) * radius;
      const z = -Math.cos(angle) * radius + 2.6;
      const y = ((idx % 3) - 1) * 0.35;

      const originalPos = new THREE.Vector3(x, y, z);
      const originalRot = new THREE.Euler(0.12, -angle * 0.85, (idx % 2 === 0 ? 0.04 : -0.04));

      mesh.position.copy(originalPos);
      mesh.rotation.copy(originalRot);

      // Target position when converging
      let targetPos = originalPos.clone();
      let targetRot = originalRot.clone();

      if (isActive) {
        targetPos = new THREE.Vector3(0, 0.48, 3.55);
        targetRot = new THREE.Euler(0, 0, 0);
      } else {
        const spreadFactor = 1.35;
        targetPos = new THREE.Vector3(x * spreadFactor, y * 0.8 - 0.4, z - 2.2);
        targetRot = new THREE.Euler(0.2, -angle * 1.05, 0.08);
      }

      mesh.userData = { act, actId: act.id, index: idx };

      planes.push({
        mesh,
        border,
        shadowMesh,
        act,
        targetPos,
        targetRot,
        originalPos,
        originalRot,
        texture: normalTex,
        activeTexture: activeTex,
        mat
      });

      planeGroup.add(mesh);
    });

    // Precision Raycasting & Click Handling
    const raycaster = new THREE.Raycaster();
    raycaster.params.Line = { threshold: 0.1 };
    let isPointerDown = false;
    let pointerDownPos = { x: 0, y: 0 };
    let dragRotY = 0;
    let targetRotY = 0;

    const getRaycastHit = (clientX: number, clientY: number) => {
      const rect = renderer.domElement.getBoundingClientRect();
      const mouse = new THREE.Vector2();
      mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const meshesToTest = planes.map(p => p.mesh);
      const intersects = raycaster.intersectObjects(meshesToTest, false);

      if (intersects.length > 0) {
        const hitMesh = intersects[0].object as THREE.Mesh;
        const act = hitMesh.userData?.act as BareAct | undefined;
        return act || null;
      }
      return null;
    };

    const handlePointerMove = (e: MouseEvent | PointerEvent) => {
      const act = getRaycastHit(e.clientX, e.clientY);
      if (act) {
        setHoveredAct(act);
        renderer.domElement.style.cursor = 'pointer';
      } else {
        setHoveredAct(null);
        renderer.domElement.style.cursor = isPointerDown ? 'grabbing' : 'grab';
      }

      if (isPointerDown) {
        const deltaX = e.clientX - pointerDownPos.x;
        targetRotY = dragRotY + deltaX * 0.005;
      }
    };

    const handlePointerDown = (e: MouseEvent | PointerEvent) => {
      isPointerDown = true;
      pointerDownPos = { x: e.clientX, y: e.clientY };
      dragRotY = targetRotY;
      renderer.domElement.style.cursor = 'grabbing';
    };

    const handlePointerUp = (e: MouseEvent | PointerEvent) => {
      isPointerDown = false;
      renderer.domElement.style.cursor = 'grab';

      // Check if it was a distinct click (distance moved < 8px)
      const dist = Math.hypot(e.clientX - pointerDownPos.x, e.clientY - pointerDownPos.y);
      if (dist < 8) {
        const clickedAct = getRaycastHit(e.clientX, e.clientY);
        if (clickedAct) {
          setSelectedActState(clickedAct.id);
          setInteractionHint(`Opening full statutory dossier for ${clickedAct.title}...`);
          if (onSelectAct) onSelectAct(clickedAct.id);
          if (onInspectAct) onInspectAct(clickedAct);
        }
      }
    };

    const domEl = renderer.domElement;
    domEl.addEventListener('pointermove', handlePointerMove);
    domEl.addEventListener('pointerdown', handlePointerDown);
    window.addEventListener('pointerup', handlePointerUp);

    // Intersection Observer to pause rendering when offscreen
    let isVisible = true;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          isVisible = entry.isIntersecting;
        });
      },
      { threshold: 0.05 }
    );
    observer.observe(container);

    // Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      if (!isVisible) return; // Skip rendering when scrolled offscreen!

      const elapsedTime = clock.getElapsedTime();

      // Smooth camera/group rotational sway + drag inertia
      planeGroup.rotation.y = THREE.MathUtils.lerp(
        planeGroup.rotation.y,
        targetRotY + Math.sin(elapsedTime * 0.35) * 0.04,
        0.08
      );

      planes.forEach((p) => {
        const isActive = p.act.id === selectedActState;
        const isHovered = hoveredAct?.id === p.act.id;

        const desiredTex = isActive ? p.activeTexture : p.texture;
        if (p.mat.map !== desiredTex) {
          p.mat.map = desiredTex;
          p.mat.needsUpdate = true;
        }

        let targetP: THREE.Vector3;
        let targetR: THREE.Euler;

        if (isActive) {
          targetP = new THREE.Vector3(0, 0.48, 3.55);
          targetR = new THREE.Euler(0, 0, 0);
          (p.border.material as THREE.LineBasicMaterial).color.setHex(0xC84B31);
          (p.border.material as THREE.LineBasicMaterial).opacity = 1.0;
        } else {
          const spreadFactor = isHovered ? 1.15 : 1.35;
          targetP = isConverging 
            ? new THREE.Vector3(p.originalPos.x * spreadFactor, p.originalPos.y * 0.85 - 0.4, p.originalPos.z - 2.2) 
            : p.originalPos;
          targetR = isConverging ? new THREE.Euler(0.2, p.originalRot.y * 1.1, 0.08) : p.originalRot;
          
          if (isHovered) {
            targetP.y += 0.3;
            targetP.z += 0.5;
            (p.border.material as THREE.LineBasicMaterial).color.setHex(0x121820);
            (p.border.material as THREE.LineBasicMaterial).opacity = 0.9;
          } else {
            (p.border.material as THREE.LineBasicMaterial).color.setHex(0x8896A6);
            (p.border.material as THREE.LineBasicMaterial).opacity = 0.4;
          }
        }

        p.mesh.position.lerp(targetP, 0.09);
        p.mesh.quaternion.slerp(new THREE.Quaternion().setFromEuler(targetR), 0.09);

        // Hover / Active floating bob
        if (isActive) {
          p.mesh.position.y += Math.sin(elapsedTime * 2.2) * 0.04;
        } else if (isHovered) {
          p.mesh.position.y += Math.sin(elapsedTime * 3.0) * 0.03;
        }

        // Active card physical emphasis (scale-up 4.5% for active, 2% for hover)
        const targetScale = isActive ? 1.045 : (isHovered ? 1.02 : 1.0);
        p.mesh.scale.setScalar(THREE.MathUtils.lerp(p.mesh.scale.x, targetScale, 0.1));

        // Depth-based opacity and atmospheric fog fade
        if (!isActive) {
          const depthFactor = THREE.MathUtils.clamp((p.mesh.position.z + 1.8) / 3.6, 0.45, 1.0);
          p.mat.opacity = THREE.MathUtils.lerp(p.mat.opacity, 0.72 + 0.28 * depthFactor, 0.1);
          (p.border.material as THREE.LineBasicMaterial).opacity = THREE.MathUtils.lerp(
            (p.border.material as THREE.LineBasicMaterial).opacity,
            (isHovered ? 0.9 : 0.25 * depthFactor + 0.15),
            0.1
          );
        } else {
          p.mat.opacity = 1.0;
        }

        // Contact shadow tracking card dynamic position & yaw
        p.shadowMesh.position.x = THREE.MathUtils.lerp(p.shadowMesh.position.x, p.mesh.position.x, 0.1);
        p.shadowMesh.position.z = THREE.MathUtils.lerp(p.shadowMesh.position.z, p.mesh.position.z, 0.1);
        p.shadowMesh.rotation.z = -p.mesh.rotation.y;

        // Shadow scale and opacity based on lift height
        if (isActive) {
          p.shadowMesh.scale.set(1.45, 1.35, 1);
          (p.shadowMesh.material as THREE.MeshBasicMaterial).opacity = 0.22;
        } else if (isHovered) {
          p.shadowMesh.scale.set(1.22, 1.15, 1);
          (p.shadowMesh.material as THREE.MeshBasicMaterial).opacity = 0.18;
        } else {
          const depthFactor = THREE.MathUtils.clamp((p.mesh.position.z + 2.0) / 4.0, 0.35, 1.0);
          p.shadowMesh.scale.set(1.0, 0.95, 1);
          (p.shadowMesh.material as THREE.MeshBasicMaterial).opacity = 0.13 * depthFactor;
        }
      });

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const newW = container.clientWidth || 600;
      const newH = container.clientHeight || 400;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };

    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container);

    return () => {
      observer.disconnect();
      cancelAnimationFrame(animationFrameId);
      resizeObserver.disconnect();
      domEl.removeEventListener('pointermove', handlePointerMove);
      domEl.removeEventListener('pointerdown', handlePointerDown);
      window.removeEventListener('pointerup', handlePointerUp);
      if (domEl && container.contains(domEl)) {
        container.removeChild(domEl);
      }
      planes.forEach(p => {
        p.texture.dispose();
        p.activeTexture.dispose();
        p.mat.dispose();
        (p.shadowMesh.material as THREE.Material).dispose();
      });
      shadowTexture.dispose();
      groundTexture.dispose();
      groundMat.dispose();
      renderer.dispose();
    };
  }, [selectedActState, isConverging, onSelectAct, onInspectAct, prefersReducedMotion, force2DMode]);

  const currentAct = BARE_ACTS_CATALOG.find(a => a.id === (hoveredAct?.id || selectedActState)) || BARE_ACTS_CATALOG[0];

  // 2D Ledger Fallback View
  if (prefersReducedMotion || !isWebGlSupported || force2DMode) {
    return (
      <div className={`relative border border-rule bg-paper p-4 sm:p-5 rounded-[2px] flex flex-col justify-between overflow-hidden ${className}`}>
        <div>
          <div className="flex flex-wrap items-center justify-between border-b border-rule pb-3 mb-3 gap-2">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-accent"></span>
              <span className="text-xs text-ink font-bold tracking-wider uppercase">
                STATUTORY RETRIEVAL ARRAY // 93 BARE ACTS LEDGER
              </span>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setForce2DMode(false)}
                className="px-2.5 py-1 text-xs border border-dark bg-white hover:bg-paper-sunken text-ink rounded-[2px] transition-colors cursor-pointer"
              >
                SWITCH TO 3D VIEW
              </button>
              <span className="text-[12px] text-ink-muted">HIGH PERFORMANCE</span>
            </div>
          </div>

          {/* 93 -> 34 -> 1 Narrowing Counter */}
          <div className="mb-3 p-2.5 bg-white border border-rule rounded-[2px] flex items-center justify-between text-xs">
            <span className="text-ink-muted">RRF CONVERGENCE:</span>
            <div className="flex items-center space-x-2">
              <span className="bg-dark text-white px-2 py-0.5 rounded-[2px]">93 CORPUS</span>
              <span>→</span>
              <span className="bg-dark text-white px-2 py-0.5 rounded-[2px]">34 BM25</span>
              <span>→</span>
              <span className="bg-accent text-white px-2 py-0.5 rounded-[2px] font-bold">1 ACTIVE</span>
            </div>
          </div>
        </div>

        {/* Scrollable Card Grid fully contained inside box boundary */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 flex-1 min-h-0 overflow-y-auto pr-1 pb-1">
          {BARE_ACTS_CATALOG.map((act) => {
            const isMatch = act.id === selectedActState;
            return (
              <button
                key={act.id}
                onClick={() => {
                  setSelectedActState(act.id);
                  if (onSelectAct) onSelectAct(act.id);
                  if (onInspectAct) onInspectAct(act);
                }}
                className={`text-left p-3 border transition-all text-xs rounded-[2px] group focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none cursor-pointer ${
                  isMatch
                    ? 'border-accent bg-white shadow-xs ring-1 ring-accent/30 font-medium'
                    : 'border-rule bg-paper-sunken/70 hover:bg-white hover:border-dark'
                }`}
              >
                <div className="flex items-center justify-between text-[12px] text-ink-muted">
                  <span>{act.actCode}</span>
                  <span className="text-accent font-bold group-hover:underline">INSPECT ACT →</span>
                </div>
                <div className="font-serif font-bold text-sm text-ink mt-0.5 line-clamp-1">{act.title}</div>
                <div className="text-[12px] text-ink-tertiary mt-1 line-clamp-1">{act.summary}</div>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className={`relative overflow-hidden border border-rule bg-paper bg-[radial-gradient(#D5CEC2_1px,transparent_1px)] [background-size:16px_16px] rounded-[2px] flex flex-col ${className}`}>
      {/* Subtle tabletop warm horizon gradient overlay */}
      <div 
        aria-hidden="true" 
        className="absolute inset-0 pointer-events-none bg-gradient-to-b from-paper/40 via-transparent to-paper-sunken/70 z-0" 
      />

      {/* Top Technical Metadata Bar & 93 -> 34 -> 1 Live Counter */}
      <div className="absolute top-0 left-0 right-0 z-20 flex items-center justify-between px-3 sm:px-4 py-2 bg-paper/95 backdrop-blur-xs border-b border-rule">
        <div className="flex items-center space-x-2">
          <span className="inline-block w-2 h-2 rounded-full bg-accent animate-pulse"></span>
          <span className="text-[12px] font-bold text-ink tracking-wider uppercase hidden sm:inline">
            3D STATUTORY ARRAY
          </span>
          <span className="text-[12px] bg-dark text-white px-2 py-0.5 rounded-[2px] font-bold">
            93 → 34 → 1 CONVERGENCE
          </span>
        </div>

        <div className="flex items-center space-x-2 text-[12px] text-ink-muted">
          <button
            onClick={() => setForce2DMode(true)}
            className="px-2 py-0.5 border border-rule bg-white hover:bg-paper-sunken text-ink rounded-[2px] transition-colors cursor-pointer"
            title="Switch to 2D ledger view for low-power devices"
          >
            2D LEDGER
          </button>
          <span className="text-ink font-bold hidden md:inline">
            ACTIVE: {selectedActState.toUpperCase()}
          </span>
        </div>
      </div>

      {/* 3D Canvas Mount Point */}
      <div 
        ref={mountRef} 
        className="w-full h-full min-h-[380px] touch-none" 
        title="Click any document plane to inspect its grounded sections or drag to rotate scene"
      />

      {/* Interactive Quick Act Selector Pill Carousel under 3D Scene */}
      <div className="absolute top-12 left-3 right-3 z-10 flex items-center space-x-1.5 overflow-x-auto pb-1 scrollbar-none pointer-events-auto">
        {BARE_ACTS_CATALOG.slice(0, 6).map((act) => (
          <button
            key={act.id}
            onClick={() => {
              setSelectedActState(act.id);
              if (onSelectAct) onSelectAct(act.id);
              if (onInspectAct) onInspectAct(act);
            }}
            className={`px-2.5 py-1 text-[12px] rounded-[2px] border shrink-0 transition-all cursor-pointer ${
              act.id === selectedActState
                ? 'bg-accent text-white border-accent font-bold shadow-xs'
                : 'bg-white/90 hover:bg-white text-ink border-rule-strong'
            }`}
          >
            {act.actCode}
          </button>
        ))}
      </div>

      {/* Bottom Floating Hover / Inspection Action Badge */}
      <div className="absolute bottom-3 left-3 right-3 z-20 flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        <div 
          onClick={() => {
            if (onInspectAct) onInspectAct(currentAct);
          }}
          className="bg-dark hover:bg-dark-rule text-paper px-3.5 py-2 rounded-[2px] text-xs shadow-md flex items-center space-x-2.5 pointer-events-auto cursor-pointer transition-colors border border-rule-dark group"
          title="Click to inspect this Act's full statutory text"
        >
          <span className="w-2 h-2 rounded-full bg-accent group-hover:scale-125 transition-transform"></span>
          <span className="text-accent font-bold uppercase tracking-wider">INSPECT:</span>
          <span className="line-clamp-1 font-serif text-sm text-white font-bold group-hover:text-paper">
            {currentAct.title}
          </span>
          <span className="text-[12px] text-slate hidden sm:inline underline">
            [OPEN DOSSIER]
          </span>
        </div>

        <button
          onClick={() => {
            if (onInspectAct) onInspectAct(currentAct);
          }}
          className="pointer-events-auto text-[12px] font-bold text-white bg-accent hover:bg-accent-hover px-4 py-2 border border-accent-hover rounded-[2px] shadow-sm flex items-center space-x-1.5 transition-all cursor-pointer active:translate-y-0.5"
        >
          <Eye className="w-3.5 h-3.5 text-white" />
          <span>INSPECT STATUTE SECTIONS</span>
        </button>
      </div>
    </div>
  );
};

export const ThreeDocumentPlanes = React.memo(ThreeDocumentPlanesComponent);
