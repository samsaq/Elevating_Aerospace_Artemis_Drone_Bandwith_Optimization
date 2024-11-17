import { title } from "@/components/primitives";
import { DroneStatusCard } from "@/components/droneStatusCard";

export default function AboutPage() {
  return (
    <div>
      <h1 className={`${title()} underline underline-offset-4`}>
        Drone Status
      </h1>
      <div className="mt-8">
        <div className="flex flex-col items-center">
          <DroneStatusCard
            name="Inpection-1"
            status="Active"
            location="Left Engine 1"
            currentTask="Inspect Engine"
          />
          <DroneStatusCard
            name="Inpection-2"
            status="Charging"
            location="Right Engine 1"
            currentTask="Inspect Engine"
          />
          <DroneStatusCard
            name="Inpection-3"
            status="Maintenance"
            location="Hangar"
            currentTask="Maintenance"
          />
        </div>
      </div>
    </div>
  );
}
