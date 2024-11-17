import { NextResponse } from "next/server";
import { DamageStatusCardProps } from "@/components/damageStatusCard";

export async function GET(request: Request) {
  // Get the URL from the request
  const { searchParams } = new URL(request.url);
  const update = searchParams.get("update");

  if (update === "true") {
    // Return updated data
    return NextResponse.json<DamageStatusCardProps[]>([
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
    ]);
  }

  // Return original data if no update parameter or update is not 'true'
  return NextResponse.json<DamageStatusCardProps[]>([
    {
      damageType: "Loose Engine Cowling",
      status: "Critical",
      damageLocation: "Left Engine 1",
    },
    {
      damageType: "Dirty Windshield",
      status: "Warning",
      damageLocation: "Cockpit",
    },
  ]);
}
