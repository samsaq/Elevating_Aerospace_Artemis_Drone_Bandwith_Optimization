import { NextResponse } from "next/server";

export async function GET() {
  // Replace this with your actual data fetching logic
  const damageStatuses = [
    {
      damageType: "Loose Engine Cowling",
      status: "Critical",
      damageLocation: "Left Engine 1",
    },
    {
      damageType: "Panel Rust",
      status: "Minor",
      damageLocation: "Left Wing Tip",
    },
    {
      damageType: "Dirty Windshield",
      status: "Warning",
      damageLocation: "Cockpit",
    },
  ];

  return NextResponse.json(damageStatuses);
}
