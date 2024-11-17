import { Link } from "@nextui-org/link";
import { button as buttonStyles } from "@nextui-org/theme";

import { siteConfig } from "@/config/site";
import { title, subtitle } from "@/components/primitives";
import { GithubIcon } from "@/components/icons";

export default function Home() {
  return (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
      <div className="flex flex-col md:flex-row items-center justify-between max-w-6xl w-full px-6">
        <div className="md:w-1/2">
          <div className="inline-block max-w-xl text-center justify-center my-4">
            <div className="my-4">
              <span className={title()}>Fly&nbsp;</span>
              <span className={title({ color: "cyan" }) + " mb-8"}>
                Safe&nbsp;
              </span>
              <span className={title()}>with&nbsp;</span>
              <br />
              <span className={title({})}>DamageDetect</span>
            </div>
            <div className={subtitle({ class: "mt-4" })}>
              Do your line maintenance faster and safer than ever before.
            </div>
          </div>

          <div className="flex gap-3 justify-center">
            <Link
              isExternal
              className={buttonStyles({
                color: "primary",
                radius: "full",
                variant: "shadow",
              })}
              href={siteConfig.links.docs}
            >
              Documentation
            </Link>
            <Link
              isExternal
              className={buttonStyles({ variant: "bordered", radius: "full" })}
              href={siteConfig.links.github}
            >
              <GithubIcon size={20} />
              GitHub
            </Link>
          </div>
        </div>

        <div className="md:w-1/2 mt-8 md:mt-0">
          <img
            src="/plane_scan_image-removebackground.png"
            alt="Drone scanning airplane illustration"
            className="hidden dark:block w-full max-w-md mx-auto"
          />
          <img
            src="/plane_scan_image.webp"
            alt="Drone scanning airplane illustration"
            className="block dark:hidden w-full max-w-md mx-auto"
          />
        </div>
      </div>
    </section>
  );
}
