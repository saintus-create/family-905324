import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
	integrations: [
		starlight({
			title: 'California Family Law Research',
			description: 'A source-aware research library for California family law, court rules, legislation, institutions, and analysis.',
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/saintus-create/family-905324' },
			],
			sidebar: [
				{
					label: 'Research',
					items: [
						{ label: 'Research Workbench', slug: 'research-workbench' },
						{ label: 'Analysis', slug: 'argument-analysis' },
						{ label: 'People & Institutions', slug: 'people-institutions' },
					],
				},
				{
					label: 'Primary Authority',
					items: [
						{ label: 'Family Code', slug: 'family-code-overview' },
						{ label: 'California Rules of Court', slug: 'court-rules-overview' },
						{ label: 'Legislation', slug: 'legislation' },
					],
				},
			],
		}),
	],
});
