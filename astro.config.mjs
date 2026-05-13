import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

// https://astro.build/config
export default defineConfig({
  site: "https://opensystemstheory.org",
  vite: {
    plugins: [tailwindcss()],
  },
  // Generate static HTML to /dist; Cloudflare Pages serves it as-is.
  output: "static",
  // Trim trailing slashes from page URLs in build output? Pages default is OK.
  trailingSlash: "always",
});
