import React, { useEffect, useRef } from 'react';

export default function AdBanner() {
  const bannerRef = useRef(null);

  useEffect(() => {
    if (!bannerRef.current) return;

    bannerRef.current.innerHTML = '';

    // Assign window.atOptions explicitly for mobile JS engines compatibility
    window.atOptions = {
      'key': '4392b35be8271f6086e67682647bc7ae',
      'format': 'iframe',
      'height': 50,
      'width': 320,
      'params': {}
    };

    const invokeScript = document.createElement('script');
    invokeScript.type = 'text/javascript';
    invokeScript.src = 'https://www.highrevenueformat.com/4392b35be8271f6086e67682647bc7ae/invoke.js';
    invokeScript.async = true;

    bannerRef.current.appendChild(invokeScript);
  }, []);

  return (
    <div className="my-6 flex justify-center w-full max-w-full overflow-x-auto select-none">
      <div 
        ref={bannerRef} 
        className="w-[320px] min-w-[320px] min-h-[50px] bg-black/20 rounded-md flex justify-center items-center overflow-hidden" 
      />
    </div>
  );
}
