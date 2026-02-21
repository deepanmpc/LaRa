# LARA 3D Immersion

## Local development

Requirements:

- Node.js
- npm

Run the app:

```sh
npm install
npm run dev
```

Default dev server URL:

- http://localhost:8080

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build production assets
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Tech stack

- Vite
- React
- TypeScript
- Tailwind CSS
- shadcn/ui

## Global deployment (GitHub Pages)

This repo is configured to auto-deploy on every push to `main` using GitHub Actions.

One-time setup in GitHub:

1. Open `Settings` -> `Pages`.
2. Set `Source` to `Deploy from a branch`.
3. Select branch `gh-pages` and folder `/ (root)`.
4. Push your changes to `main`.

Public URL:

- https://visala-paladagu.github.io/lara_3d/
