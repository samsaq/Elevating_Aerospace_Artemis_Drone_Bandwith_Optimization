"use client";

import { useState, useEffect } from "react";

import { title } from "@/components/primitives";
import {
  DamageStatusCard,
  DamageStatusCardProps,
} from "@/components/damageStatusCard";

export default function AboutPage() {
  const [damageStatuses, setDamageStatuses] = useState<DamageStatusCardProps[]>(
    []
  );

  useEffect(() => {
    // Fetch damage statuses when component mounts
    fetchDamageStatuses();
  }, []);

  const fetchDamageStatuses = async () => {
    try {
      const response = await fetch("/api/damage-status"); // API endpoint
      const data = await response.json();
      setDamageStatuses(data);
    } catch (error) {
      console.error("Error fetching damage statuses:", error);
    }
  };

  return (
    <div>
      <h1 className={`${title()} underline underline-offset-4`}>
        Damage Status
      </h1>
      <div className="mt-8">
        <div className="flex flex-col items-center justify-center gap-1">
          {damageStatuses.map((status, index) => (
            <DamageStatusCard
              key={index}
              damageType={status.damageType}
              status={status.status}
              damageLocation={status.damageLocation}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
