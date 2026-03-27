"use client";

import "mapbox-gl/dist/mapbox-gl.css";

import type { ReactNode } from "react";
import { useEffect, useRef } from "react";

type MapWrapperProps = {
  children?: ReactNode;
  className?: string;
};

export function MapWrapper({ children, className = "" }: MapWrapperProps) {
  const mapRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let mounted = true;

    async function initializeMap() {
      if (!mapRef.current) return;
      const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
      if (!token) return;

      const mapboxgl = (await import("mapbox-gl")).default;
      mapboxgl.accessToken = token;

      const map = new mapboxgl.Map({
        container: mapRef.current,
        style: "mapbox://styles/mapbox/light-v11",
        projection: "globe",
        center: [10, 18],
        zoom: 1.1,
      });

      map.on("style.load", () => {
        if (!mounted || !mapRef.current) return;
        map.setFog({});
      });
    }

    initializeMap();

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className={`relative overflow-hidden rounded-2xl border border-gray-100 bg-white ${className}`}>
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,#f6f6f6_1px,transparent_1px),linear-gradient(to_bottom,#f6f6f6_1px,transparent_1px)] bg-[size:26px_26px]" />
      <div ref={mapRef} className="relative h-[520px] w-full" />
      {children}
    </div>
  );
}
