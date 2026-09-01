import React, { useEffect, useRef } from 'react';

export default function AdNativeBanner() {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Clear container to prevent duplicate script execution on re-renders
    containerRef.current.innerHTML = '';

    // Create container div required by Adsterra Native Banner
    const targetDiv = document.createElement('div');
    targetDiv.id = 'container-01fc966c7ee595466e75917b5df2bdac';
    targetDiv.className = 'w-full flex justify-center items-center';

    // Create script element
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.async = true;
    script.setAttribute('data-cfasync', 'false');
    script.src = 'https://pl31126011.profitableratecpmnetwork.com/01fc966c7ee595466e75917b5df2bdac/invoke.js';

    containerRef.current.appendChild(targetDiv);
    containerRef.current.appendChild(script);
  }, []);

  return (
    <div className="my-8 flex justify-center w-full max-w-full overflow-x-auto min-h-[120px]">
      <div ref={containerRef} className="w-full flex justify-center items-center min-h-[100px]" />
    </div>
  );
}
