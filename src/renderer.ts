import App from "./components/App.svelte";


const mainPages = [
	{
		id: "Normline",
		filetag: "felix",
		filetype: "felix, cfelix",
		funcBtns: [
			{
				id: "createBaselineBtn",
				name: "Create Baseline"
			},
			{
				id: "felixPlotBtn",
				name: "Felix Plot"
			},
			{
				id: "theoryBtn",
				name: "Add Theory"
			}
		],
		plotID: ["exp-theory-plot", "bplot", "saPlot", "nplot", "avgplot"]
	},
	{
		id: "Masspec",
		filetag: "mass",
		filetype: "mass",
		funcBtns: [
			{
				id: "massPlotBtn",
				name: "Masspec Plot"
			}
		],
		plotID: ["mplot"]
	},
	{
		id: "Timescan",
		filetag: "scan",
		filetype: "scan",
		funcBtns: [
			{
				id: "timescanBtn",
				name: "Timescan Plot"
			}
		],
		plotID: ["tplot_container"]
	},
	{
		id: "THz",
		filetag: "thz",
		filetype: "thz",
		funcBtns: [
			{
				id: "thzBtn",
				name: "THz Plot"
			}
		],
		plotID: ["thzplot_Container"]
	}
];

const app = new App({
	target: document.body,
	props: { mainPages}
});

export default app;
