'use client';

import { useEffect, useState } from 'react';

interface HydrationBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

/**
 * HydrationBoundary prevents hydration mismatches by rendering a fallback
 * until the component has hydrated on the client.
 */
export function HydrationBoundary({ children, fallback = null }: HydrationBoundaryProps) {
  const [hasMounted, setHasMounted] = useState(false);

  useEffect(() => {
    setHasMounted(true);
  }, []);

  if (!hasMounted) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}