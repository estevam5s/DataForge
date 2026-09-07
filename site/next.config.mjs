/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Gera HTML estático: a documentação não precisa de servidor.
  output: 'export',
  images: { unoptimized: true },
  trailingSlash: true,
};

export default nextConfig;
