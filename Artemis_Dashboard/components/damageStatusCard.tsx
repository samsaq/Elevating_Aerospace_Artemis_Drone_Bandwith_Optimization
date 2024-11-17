import { Icon } from "@iconify/react";

import { Pulse } from "./pulse";

export interface DamageStatusCardProps {
  damageType: string;
  status: "Critical" | "Moderate" | "Minor" | "Warning";
  damageLocation: string;
}

export const DamageStatusCard = ({
  damageType,
  status,
  damageLocation,
}: DamageStatusCardProps) => {
  const statusColors = {
    Critical: "bg-red-500",
    Moderate: "bg-orange-500",
    Minor: "bg-yellow-500",
    Warning: "bg-cyan-500",
  };

  return (
    <div className="bg-foreground/10 rounded-lg p-6 relative m-4 inline-block w-[700px]">
      <div className="flex justify-between px-4">
        <div className="flex justify-between items-start mr-8">
          <div className="flex gap-8">
            {/* Damage Type Section */}
            <div className="flex flex-col whitespace-nowrap">
              <h3 className="text-sm font-medium text-foreground/60">Damage</h3>
              <p className="text-foreground">{damageType}</p>
            </div>

            {/* Status Section */}
            <div className="flex flex-col whitespace-nowrap">
              <h3 className="text-sm font-medium text-foreground/60">Status</h3>
              <p className="text-foreground">{status}</p>
            </div>

            {/* Location Section */}
            <div className="flex flex-col whitespace-nowrap">
              <h3 className="text-sm font-medium text-foreground/60">
                Location
              </h3>
              <p className="text-foreground">{damageLocation}</p>
            </div>
          </div>
        </div>
        <div className="flex justify-between items-center pr-2">
          {/* Action Buttons */}
          <div className="flex flex-col gap-2">
            <button className="absolute top-2 right-2">
              <Icon icon="mdi:gear" className="h-4 w-4 text-foreground/60" />
            </button>

            <div className="absolute top-2 left-2">
              <Pulse color={statusColors[status]} />
            </div>

            <div className="flex gap-2">
              <button className="px-3 py-1 rounded bg-green-500/20 text-green-500 hover:bg-green-500/30 transition">
                Confirm
              </button>
              <button className="px-3 py-1 rounded bg-red-500/20 text-red-500 hover:bg-red-500/30 transition">
                Deny
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
