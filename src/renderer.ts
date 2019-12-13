
import App from "./components/App.svelte";

let shell_help = "Open terminal while plotting in Matplotlib. Turn this ON to check for any error occured from python console."
const mainPages = [

	// FELIX plot and baseline correction

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
			},
			{
				id: "norm_tkplot",
				name: "Open in matplotlib"
			}
		],
		plotID: ["exp-theory-plot", "bplot", "saPlot", "avgplot", "opoplot"],
		checkBtns: [
			{
				id: "felix_shell",
				name: ["", ""],
				bind: false,
				help:shell_help
			
			}
		]
	},

	// Masspec plot

	{
		id: "Masspec",
		filetag: "mass",
		filetype: "mass",
		funcBtns: [
			{
				id: "massPlotBtn",
				name: "Masspec Plot",
			},
			{
				id: "mass_find_peaks",
				name: "Find Peaks"
			},
			{
				id: "nist_webbook",
				name: "NIST Webbook"
			},
			{
				id: "mass_Matplotlib",
				name: "Open in matplotlib"
			}
			
		],
		plotID: ["mplot"],
		checkBtns: [
			{
				id: "mass_shell",
				name: ["", ""],
				bind: false,
				help:shell_help
			},
			{
				id: "masslinearlog",
				name: ["Log", "Linear"],
				bind:true,
				help:"Plot the Yscale in Log/Linear"
			}
		]
	},
	
	// Timescan plot

	{
		id: "Timescan",
		filetag: "scan",
		filetype: "scan",
		funcBtns: [
			{
				id: "timescanBtn",
				name: "Timescan Plot"
			}, 
			{
				id: "depletionscanBtn",
				name: "Depletion Plot"
			},
			{
				id: "scan_Matplotlib",
				name: "Open in matplotlib"
			}
		],
		plotID: ["tplot_container"],
		checkBtns: [
			{
				id: "scan_shell",
				name: ["", ""],
				bind:false,
				help:shell_help
			},
			{
				id: "scanlinearlog",
				name: ["Log", "Linear"],
				bind:false,
				help:"Plot the Yscale in Log/Linear"
			}
		]
	},

	// THz plot

	{
		id: "THz",
		filetag: "thz",
		filetype: "thz",
		funcBtns: [
			{
				id: "thzBtn",
				name: "THz Plot"
			},
			{
				id: "thz_Matplotlib",
				name: "Open in matplotlib"
			}
		],
		plotID: ["thzplot_Container"],
		checkBtns: [
			{
				id: "thz_shell",
				name: ["", ""],
				bind:false,
				help:shell_help
			}
		]
	}
];

const app = new App({
	target: document.body,
	props: { mainPages}
});

export default app;
