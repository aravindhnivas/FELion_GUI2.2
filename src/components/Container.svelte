<script>
  // Importing Svelte modules
  import Filebrowser from "./utils/Filebrowser.svelte";
  import { runPlot } from "./utils/js/felion_main.js";

  import * as dirTree from "directory-tree";

  export let id;
  export let filetag;
  export let filetype;
  export let funcBtns;
  export let plotID;
  export let jq;
  export let electron;
  export let path;
  const dialog = electron.remote.dialog;

  jq(document).ready(() => {
    jq("#theoryBtn")
      .addClass("fadeInUp").css("display", "none");
  });

  const join = file => {
    return [path.join(currentLocation, file)];
  };
  let delta = 1;
  const changeDelta = event => {
    if (event.key == "Enter") {
      runPlot({
        fullfiles: fullfiles,
        filetype: filetag,
        btname: "felixPlotBtn",
        pyfile: "normline.py",
        normethod: normlog,
        args: delta
      });
    }
  };

  let normMethod = "Log";
  let normlog = true;
  $: normMethod == "Relative" ? (normlog = false) : (normlog = true);
  let log;
  $: filetag == "mass" ? (log = true) : (log = false);

  const linearlogCheck = event => {
    let target = event.target;
    let layout = {
      yaxis: {
        title: "Counts",
        type: target.checked ? "log" : null
      }
    };
    if (filetag == "mass") {
      Plotly.relayout("mplot", layout);
    } else {
      fileChecked.forEach(file => {
        let tplot = file + "_tplot";
        Plotly.relayout(tplot, layout);
      });
    }
  };

  let folderFile = { folders: [], files: [] };

  let tree = dirTree.default;
  const style = "display:none;";
  let currentLocation;

  let allFiles = [];
  $: fileChecked = allFiles.filter(file => file.checked).map(file => file.id);
  $: console.log("fileChecked", fileChecked);
  $: fullfiles = fileChecked.map(file => path.join(currentLocation, file));

  const getCheckedFiles = () => {
    allFiles = Array.from(document.querySelectorAll("." + filetag + "-files"));
  };

  const updateFolder = location => {
    console.log("Folder updating");
    currentLocation = location;

    if (currentLocation == undefined) {
      jq(`#${filetag}refreshIcon`).removeClass("fa-spin");
      console.log("Location undefined");
      return undefined;
    }

    jq(`#${filetag}refreshIcon`).addClass("fa-spin");

    let folder = [];
    let file = [];

    const folderTree = tree(
      currentLocation,
      { extensions: new RegExp(filetag) },
      (item, PATH, stats) => {
        console.log(item);
      }
    );

    let folderChild = folderTree.children;
    for (let i in folderChild) {
      folderChild[i].type == "file"
        ? (file = [folderChild[i].name, ...file])
        : (folder = [folderChild[i].name, ...folder]);
    }
    folderFile.parentFolder = folderTree.name;
    folderFile.folders = folder;
    folderFile.files = file;

    console.log("Folder updated");

    jq(`#${filetag}refreshIcon`).removeClass("fa-spin");
    return folderFile;
  };

  function browseFile({theory=false}) {

    if (theory == true) {
      return new Promise((resolve, reject) => {
        let files;

        console.log("Optional file");
        const options = {
          title: `Open theory files`,
          filters: [{ name: "All files", extensions: ["*"] }],
          properties: ["openFile", "multiSelections"],
          message: `Open theory files` //For macOS
        };
        dialog.showOpenDialog(null, options, filePaths => {
          if (filePaths == undefined) reject("No files selected");

          resolve(filePaths);
        });
      });
    } else {
      const options = {
        title: `Open ${filetag} files`,
        filters: [
          { name: `${filetag} files`, extensions: filetype.split(", ") },
          { name: "All files", extensions: ["*"] }
        ],
        properties: ["openFile", "multiSelections"],
        message: `Open ${filetag} files` //For macOS
      };
      dialog.showOpenDialog(null, options, filePaths => {
        if (filePaths == undefined) return console.log("No files selected");
        currentLocation = path.dirname(filePaths[0]);
        folderFile = updateFolder(currentLocation);
      });
    }
  }

  const functionRun = event => {
    let btname = event.target.id;
    if (btname == "felixPlotBtn") {

      Plotly.purge("exp-theory-plot");
      runPlot({
        fullfiles: fullfiles, filetype: filetag, btname: btname,
        pyfile: "normline.py", normethod: normlog, args: delta
      });


    }
      
    if (btname == "createBaselineBtn")
      runPlot({
        fullfiles: fullfiles,
        filetype: "general",
        btname: btname,
        pyfile: "baseline.py"
      });
    if (btname == "massPlotBtn")
      runPlot({
        fullfiles: fullfiles,
        filetype: filetag,
        btname: btname,
        pyfile: "mass.py"
      });
    if (btname == "timescanBtn") {
      fileChecked.forEach(file => {
        runPlot({
          fullfiles: join(file),
          filetype: filetag,
          btname: btname,
          pyfile: "timescan.py",
          plotArea: file + "_tplot"
        });
      });
    }
    if (btname == "thzBtn") {
      fileChecked.forEach(file => {
        runPlot({
          fullfiles: join(file),
          filetype: filetag,
          btname: btname,
          pyfile: "thz_scan.py",
          plotArea: file + "_plot"
        });
      });
    }
    if (btname == "theoryBtn") jq("#theoryRow").toggle()
    if (btname == "depletionscanBtn") jq("#depletionRow").toggle()
  };

  let theoryfiles=[];
  $: theoryfilenames = theoryfiles.map(file=>path.basename(file))
  
  function opentheory() {
    browseFile({theory:true})
      .then(file =>  theoryfiles = file).catch(err => console.log(err));
  }


  function runtheory() {
    runPlot({fullfiles: theoryfiles, filetype: "theory", 
      btname: "appendTheory", pyfile: "theory.py", args: [normMethod, sigma, scale, currentLocation] });
  }
  const runtheory_keyup = (event) => {if(event.key=="Enter") runtheory()}
  let sigma=20; //Sigma value for felixplot thoery gaussian profile
  let scale=1;

  // let resOnFile="onFile";
  // let resOffFile="offFile";
  let powerinfo = "21, 21";
  let nshots = 10;
  let massIndex = 0;
  let timestartIndex = 1;

  let depletionLabels = [
    {
      name: "Power (ON, OFF)",
      id: "powerinfo",
      value:powerinfo
    },
    {
      name: "FELIX Hz",
      id: "nshots",
      value:nshots
    },
    {
      name: "Mass Index",
      id: "massIndex",
      value:massIndex
    },
    {
      name: "TimeStart Index",
      id: "timeIndex",
      value:timestartIndex
    }
  ]

  const depletionPlot = () => {

    runPlot({fullfiles: [currentLocation], filetype: "general", 
      btname: "depletionSubmit", pyfile: "depletionscan.py", args: [jq(ResON).val(), jq(ResOFF).val(), powerinfo, nshots, massIndex, timestartIndex] });
  }
</script>

<style>
  label {color:white;}
  #theorylabel{
    color:white;
    border:solid 3px #bdc3c7; 
    padding:0.4em;
  }
  .locationLabel {
    text-align: center;
  }
  .row {
    display: flex;
    flex-direction: column;
    padding-bottom: 2em;
  }
  .funcBtn {
    margin: 0 0.5em;
  }

  .section {
    position: fixed;
    width: 100%;
  }
  .plotContainer {
    overflow-y: auto;
    max-height: 38rem;
    width: 70%;
    position: absolute;
  }
  img {
    width: 20%;
    margin-left: 40%;
  }
  .data-loading {
    display: none;
  }

  @media (max-width: 1200px) {
    .plotContainer {
      max-height: 27rem;
    }
  }

  #theoryContainer {
    margin-left: 20%;
    margin-right:20%;
  }
</style>

<section class="section" {id} {style}>

  <div class="columns">

    <div class="column is-3" id="{filetag}filebrowserColumn">
      <Filebrowser
        {filetag} {currentLocation} {updateFolder}
        {getCheckedFiles} {jq} {path} />
    </div>

    <div class="column">

      <div class="row">
        <div class="field has-addons">
          <div class="control is-expanded">
            <input
              class="input locationLabel"
              type="text"
              placeholder="Location will be displayed"
              id="{filetag}LocationLabel"
              bind:value={currentLocation} />
          </div>
          <div class="control">
            <div
              class="button is-dark"
              on:click={browseFile}
              data-tippy="Browse {filetag} file">
              Browse
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="level">
          <div class="level-left animated fadeIn">

            {#each funcBtns as { id, name }}
              <div
                class="level-item button funcBtn is-link animated"
                {id}
                on:click={functionRun}>
                {name}
              </div>
            {/each}

            {#if filetag == 'felix'}
              <div class="level-item">
                <div class="field has-addons">
                  <div class="control">
                    <span class="select">
                      <select
                        id="felixmethod"
                        bind:value={normMethod}
                        data-tippy="Normalisation method">
                        <option>Relative</option>
                        <option>Log</option>
                      </select>
                    </span>
                  </div>
                  <div class="control">
                    <input
                      class="input"
                      type="number" step="0.5"
                      id="delta_value"
                      placeholder="Delta value"
                      data-tippy="Delta value for averaging FELIX spectrum"
                      bind:value={delta}
                      on:keyup={changeDelta} />
                  </div>
                </div>
              </div>
            {/if}

            {#if filetag == 'mass' || filetag == 'scan'}
              <div class="level-item">
                <div class="pretty p-default p-curve p-toggle">
                  <input
                    type="checkbox"
                    id="{filetag}linearlog"
                    bind:checked={log}
                    on:click={linearlogCheck} />
                  <div class="state p-success p-on">
                    <label>Log</label>
                  </div>
                  <div class="state p-danger p-off">
                    <label>Linear</label>
                  </div>
                </div>
              </div>
            {/if}

          </div>
        </div>

      </div>

      {#if filetag=="felix"}
         <div class="row" id="theoryRow" style="display:none">
            <div class="container" id="theoryContainer">
              <div class="field">
                <label class="label" id="theorylabel">
                  <h1 class="subtitle" id="theoryfilename">{theoryfilenames}</h1>
                </label>
                <div class="control">
                    <button class="button is-warning" on:click={opentheory}>Choose file</button>
                    <input class="input" type="number" on:keyup={runtheory_keyup} bind:value={sigma} style="width:150px" data-tippy="Sigma (deviation) from central frequency">
                    <input class="input" type="number" on:keyup={runtheory_keyup} step="0.001" bind:value={scale} style="width:150px" data-tippy="Scaling factor (to shift in position)">
                    <button class="funcBtn button is-link animated" on:click={runtheory} id="appendTheory">Submit</button>
                </div>
              </div>
            </div>
         </div>
      {/if}

      {#if filetag=="scan"}
         <div class="row" id="depletionRow">
            <div class="level">
              <div class="level-left">

                {#each ["ResON", "ResOFF"] as name}

                  <div class="level-item">
                    <div class="field">
                      <label class="label"><h1 class="subtitle">{name} file</h1></label>
                      <div class="control">
                        <div class="select">
                          <select id={name}>
                            {#if folderFile.files != undefined}
                               {#each folderFile.files as scanfile}
                                  <option value={scanfile}>{scanfile}</option>
                               {/each}
                            {/if}
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                {/each}

                {#each depletionLabels as {name, id, value}}
                  <div class="level-item">
                    <div class="field">
                      <label class="label"><h1 class="subtitle">{name}</h1></label>
                      <div class="control">
                          <input class="input" bind:value={value} {id}>
                      </div>
                    </div>
                  </div>
                {/each}
              
              </div>
            </div>

            <div class="control">
              <button class="funcBtn button is-link animated" id="depletionSubmit" on:click={depletionPlot}>Submit</button>
            </div>
         </div>
      {/if}

      <hr style="margin: 0.5em 0; background-color:#bdc3c7" />
      <h1 class="subtitle">Data Visualisation</h1>

      <div class="row box plotContainer">
        <img
          class="data-loading"
          id="{filetag}loading"
          src="./icons/loadingBar.svg"
          alt="loading data" />
        <div class="container is-fluid" id="{filetag}plotContainer">
          {#each plotID as id}
            {#if filetag == 'scan'}
              <div {id} style="padding-bottom:1em">
                {#each fileChecked as scanfile}
                  <div id="{scanfile}_tplot" style="padding-bottom:1em" />
                {/each}
              </div>
            {:else if filetag == 'thz'}
              <div {id} style="padding-bottom:1em">
                {#each fileChecked as thzfile}
                  <div id="{thzfile}_plot" style="padding-bottom:1em" />
                {/each}
              </div>
            {:else}
              <div {id} style="padding-bottom:1em" />
            {/if}
          {/each}
        </div>
      </div>

    </div>

  </div>
</section>
