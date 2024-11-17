"use client";

import { useState, useEffect } from "react";

import { title } from "@/components/primitives";
import {
  DamageStatusCard,
  DamageStatusCardProps,
} from "@/components/damageStatusCard";

import { Icon } from "@iconify/react";

export default function AboutPage() {
  const [isUpdated, setIsUpdated] = useState(false);
  const [damageStatuses, setDamageStatuses] = useState<DamageStatusCardProps[]>(
    []
  );

  useEffect(() => {
    // Fetch damage statuses when component mounts
    fetchDamageStatuses();
  }, []);

  const fetchDamageStatuses = async (update: boolean = false) => {
    try {
      const response = await fetch(
        `/api/damage-status${update ? "?update=true" : ""}`
      );
      const data = await response.json();
      setDamageStatuses(data);
      setIsUpdated(update);
    } catch (error) {
      console.error("Error fetching damage statuses:", error);
    }
  };

  return (
    <div>
      <div className="flex items-center gap-4 justify-center">
        <h1 className={`${title()} underline underline-offset-4`}>
          Damage Status
        </h1>
        <Icon
          icon="material-symbols-light:refresh"
          onClick={() => fetchDamageStatuses(!isUpdated)}
          className="w-8 h-8 p-1 text-2xl cursor-pointer rounded-full hover:bg-default-200 transition-colors"
        />
      </div>
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
