/// <reference types="vite/client" />
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import viteTsconfigPaths from "vite-tsconfig-paths";
import svgr from "vite-plugin-svgr";
import fs from "fs";



// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(),"VITE_");
	const rewriteRegex = new RegExp(
		String.raw`^/api/${env.VITE_API_VERSION}`
	);

	const config = {
		server: {
			port: 3000,
			strictPort: true,
			https: mode === "development" ? {
				key: fs.readFileSync(env.VITE_SSL_PRIVATE),
				cert: fs.readFileSync(env.VITE_SSL_PUBLIC),
			} : {},
			proxy: {
				"/api": {
					target: `${env.VITE_BASE_ADDRESS}`,
					changeOrigin: true,
					rewrite: (path: string) => path.replace(rewriteRegex, ""),
					secure: false,
				},
			},
		},
		plugins: [
			react(),
			viteTsconfigPaths(),
			svgr({
				include: "**/*.svg?react",
			}),
		],
		build: {
			outDir: "build",
		},
	};
	return config;
});