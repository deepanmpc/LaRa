import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(() => {
  const repositoryName = process.env.GITHUB_REPOSITORY?.split("/")[1] ?? "lara_3d";
  const isGithubActionsBuild = process.env.GITHUB_ACTIONS === "true";

  return {
    base: isGithubActionsBuild ? `/${repositoryName}/` : "/",
    server: {
      host: "::",
      port: 8080,
    },
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
  };
});
