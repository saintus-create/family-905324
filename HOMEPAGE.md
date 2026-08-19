# Homepage architecture

The real homepage is the upstream Svelte SaaS Starter, referenced at `svelte-saas-starter/` as a Git submodule. It is not recreated in Fern.

- Public homepage: <https://svelte-saas-starter.vercel.app>
- Upstream source: <https://github.com/Jeffreyyvdb/svelte-saas-starter>
- Documentation source: `fern/`
- Fern's root fallback immediately redirects to the public homepage in `fern/custom.js`.

After cloning this repository, initialize the original homepage source with:

```bash
git submodule update --init --recursive
```

To run it locally:

```bash
cd svelte-saas-starter
npm install
npm run dev
```

Do not replace `fern/docs/pages/welcome.mdx` with a hand-built imitation of the template.
