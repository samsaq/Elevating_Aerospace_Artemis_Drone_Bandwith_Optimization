export type SiteConfig = typeof siteConfig;

export const siteConfig = {
  name: "DamageDetect",
  description:
    "Fly safe with aircraft damage detection as part of your line maintenance with DamageDetect.",
  navItems: [
    {
      label: "Home",
      href: "/",
    },
    {
      label: "Dashboard",
      href: "/dashboard",
    },
    {
      label: "Drones",
      href: "/drones",
    },
  ],
  navMenuItems: [
    {
      label: "Profile",
      href: "/profile",
    },
    {
      label: "Dashboard",
      href: "/dashboard",
    },
  ],
  links: {
    github:
      "https://github.com/samsaq/Elevating_Aerospace_Artemis_Drone_Bandwith_Optimization",
    docs: "https://nextui.org",
    discord: "https://discord.gg/2bFZDA5K",
  },
};
