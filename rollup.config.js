import svelte from 'rollup-plugin-svelte';
import commonjs from 'rollup-plugin-commonjs';
import resolve from 'rollup-plugin-node-resolve';
import json from 'rollup-plugin-json';
import typescript from 'rollup-plugin-typescript';
import sveltePreprocess from 'svelte-preprocess';


const preprocess = sveltePreprocess({
	scss: {includePaths: ['src'],},
	postcss: {plugins: [require('autoprefixer')],},
  });

export default {
	

	input: ['src/main.ts', 'src/renderer.ts'],

	output: {
		dir: 'dist',
		format: 'cjs',
		sourcemap: true
	},

	plugins: [
		resolve(),
		svelte({
			css(css) {css.write('dist/svelte.css');},
			preprocess,
		}),
		commonjs(),
		json(),
		typescript({ typescript: require('typescript') })
	],

	external: [
		'electron',
		'child_process',
		'fs',
		'path',
		'url',
		'module',
		'os'
	]
};
