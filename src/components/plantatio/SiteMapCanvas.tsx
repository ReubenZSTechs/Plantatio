import { useMemo } from "react";
import { GeoJSON, MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import { potentialColor, type SiteMapProps } from "./SiteMap";

/**
 * Leaflet's default marker icons resolve against a relative sprite path that
 * does not survive bundling, so markers are drawn as inline SVG instead.
 */
function nodeIcon(status: string): L.DivIcon {
  const fill = status === "critical" ? "#dc2626" : status === "warn" ? "#d97706" : "#16a34a";

  return L.divIcon({
    className: "",
    iconSize: [18, 18],
    iconAnchor: [9, 9],
    html: `<span style="display:block;width:18px;height:18px;border-radius:9999px;background:${fill};border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,.4)"></span>`,
  });
}

/** The browser-only half of SiteMap. Never imported on the server. */
export function SiteMapCanvas({
  parcels = [],
  nodes = [],
  selectedParcelId = null,
  onSelectParcel,
  className,
}: SiteMapProps) {
  const center = useMemo<[number, number]>(() => {
    const points = [
      ...parcels.map((p) => [p.centroidLatitude, p.centroidLongitude] as const),
      ...nodes.map((n) => [n.latitude, n.longitude] as const),
    ];

    // Fall back to the seeded monitoring site.
    if (points.length === 0) return [-6.1754, 106.8272];

    return [
      points.reduce((sum, p) => sum + p[0], 0) / points.length,
      points.reduce((sum, p) => sum + p[1], 0) / points.length,
    ];
  }, [parcels, nodes]);

  return (
    <div className={className}>
      <MapContainer
        center={center}
        zoom={14}
        scrollWheelZoom
        className="h-full w-full rounded-xl"
        style={{ minHeight: 320 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {parcels.map((parcel) => (
          <GeoJSON
            key={`${parcel.id}-${parcel.restorationPotential}-${selectedParcelId === parcel.id}`}
            data={parcel.geometry as never}
            style={{
              color: potentialColor(parcel.restorationPotential),
              weight: selectedParcelId === parcel.id ? 4 : 2,
              fillOpacity: selectedParcelId === parcel.id ? 0.45 : 0.25,
            }}
            eventHandlers={{ click: () => onSelectParcel?.(parcel) }}
          >
            <Popup>
              <strong>{parcel.name}</strong>
              <br />
              {parcel.landCoverClass} · {parcel.areaHectares} ha
              <br />
              Potential: {((parcel.restorationPotential ?? 0) * 100).toFixed(0)}%
            </Popup>
          </GeoJSON>
        ))}

        {nodes.map((node) => (
          <Marker
            key={node.id}
            position={[node.latitude, node.longitude]}
            icon={nodeIcon(node.status)}
          >
            <Popup>
              <strong>{node.id}</strong>
              <br />
              {node.zone}
              <br />
              Moisture {node.moisture}% · Battery {node.battery}%
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
