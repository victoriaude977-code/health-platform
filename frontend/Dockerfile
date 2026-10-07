# The Vue app is prebuilt on a dev machine (npm run build) and committed
# as dist/ - the server only copies it into nginx. This keeps the server
# build tiny (no npm install / vite build on a 1 GB VM).
FROM nginx:1.27-alpine
COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
