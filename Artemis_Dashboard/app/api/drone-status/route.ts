import { NextResponse } from "next/server";

import { DroneStatusCardProps } from "@/components/droneStatusCard";

export async function GET() {
  // Drone status data
  const droneStatuses: DroneStatusCardProps[] = [
    {
      name: "Inpection-1",
      status: "Active",
      location: "Left Engine 1",
      currentTask: "Inspect Engine",
    },
    {
      name: "Inpection-2",
      status: "Charging",
      location: "Right Engine 1",
      currentTask: "Inspect Engine",
    },
    {
      name: "Inpection-3",
      status: "Maintenance",
      location: "Hangar",
      currentTask: "Maintenance",
    },
  ];

  return NextResponse.json(droneStatuses);
}
