import { fileURLToPath, URL } from 'node:url';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig(() => {
    return {
        outputDir: '../backend/templates/SPA',
        plugins: [vue()],
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url))
            }
        }
    };
});


// module.exports = {
//   outputDir: path.resolve(__dirname, "../backend/templates/SPA"),
//   assetsDir: "../../static/SPA"
// }