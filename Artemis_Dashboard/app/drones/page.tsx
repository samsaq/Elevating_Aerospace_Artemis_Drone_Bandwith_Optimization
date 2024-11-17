"use client";

import { useState, useEffect } from "react";

import { title } from "@/components/primitives";
import {
  DroneStatusCard,
  DroneStatusCardProps,
} from "@/components/droneStatusCard";

export default function DroneStatusPage() {
  const [droneStatuses, setDroneStatuses] = useState<DroneStatusCardProps[]>(
    []
  );

  useEffect(() => {
    fetchDroneStatuses();
  }, []);

  const fetchDroneStatuses = async () => {
    try {
      const response = await fetch("/api/drone-status");
      const data = await response.json();
      setDroneStatuses(data);
    } catch (error) {
      console.error("Error fetching drone statuses:", error);
    }
  };

  return (
    <div>
      <h1 className={`${title()} underline underline-offset-4`}>
        Drone Status
      </h1>
      <div className="mt-8">
        <div className="flex flex-col items-center">
          {droneStatuses.map((drone) => (
            <DroneStatusCard key={drone.name} {...drone} />
          ))}
        </div>
      </div>
    </div>
  );
}
