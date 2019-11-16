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

  export let checkBtns;
  export let jq;
  export let electron;

  export let path;
  export let menu;
  export let MenuItem;

  // export let PythonShell;

  menu.append(new MenuItem({ label: `Open ${filetag} plot in Matplotlib`, click() {

      let obj = {
        fullfiles: fullfiles,
        filetag:filetag,            
        filetype: "general",
        btname: `${filetag}_Matplotlib`,
        pyfile: fileInfo[filetag]["pyfile"],
        args: fileInfo[filetag]["args"]
      }
      runPlot(obj);
    } 
  }))
  
  $: plotContainerHeight = "60vh"

  jq(document).ready(() => {

    jq("#theoryBtn").addClass("fadeInUp").css("display", "none");
    jq("#norm_tkplot").addClass("fadeInUp").css("display", "none");

    jq("#exp_fit").addClass("fadeInUp").css("display", "none");
    jq("#felix_shell_Container").addClass("fadeInUp").css("display", "block");

  });
  
  const join = file => {
    return [path.join(currentLocation, file)];
  };

  let delta = 1;

  let normMethod = "IntensityPerPhoton";
  let normalisation_method = ["Log", "Relative", "IntensityPerPhoton"]
  
  let log;
  $: filetag == "mass" ? (log = true) : (log = false);

  const linearlogCheck = event => {

    let target = event.target;
    let layout = {
      yaxis: {
        title: "Counts",
        type: target.checked ? "log" : null
      }
    }

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
  $: console.log(`Locally stored location: [${filetag}]: ${localStorage.getItem(`${filetag}_location`)}`)

  if (localStorage.getItem(`${filetag}_location`) != undefined) {currentLocation = localStorage.getItem(`${filetag}_location`)}

  let allFiles = [];
  $: fileChecked = allFiles.filter(file => file.checked).map(file => file.id).sort();
  $: console.log("fileChecked", fileChecked, "\n");
  $: fullfiles = fileChecked.map(file => path.join(currentLocation, file));

  const getCheckedFiles = () => {
    allFiles = Array.from(document.querySelectorAll("." + filetag + "-files"));
  };

  const updateFolder = location => {
    console.log("Folder updating");

    if (location === undefined || location === 'undefined') {
      jq(`#${filetag}refreshIcon`).removeClass("fa-spin");
      console.log("Location is undefined");
      return undefined;
    } 

    currentLocation = location;
    localStorage.setItem(`${filetag}_location`, currentLocation)

    console.log(`[${filetag}]: location is stored locally\n${currentLocation}`)

    jq(`#${filetag}refreshIcon`).addClass("fa-spin");
    try {

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
    } catch (err) {console.log(`Error Occured: ${err}`)}

    jq(`#${filetag}refreshIcon`).removeClass("fa-spin");
    return folderFile;

  };
  
  let theoryfiles = [];

  if (localStorage.getItem("theoryfiles") != undefined) {theoryfiles = localStorage.getItem("theoryfiles").split(",")}
  $: theoryfilenames = theoryfiles.map(file=>path.basename(file))

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

        electron.remote.dialog.showOpenDialog(null, options, filePaths => {

          if (filePaths == undefined) {reject("No files selected")}
          else {localStorage.setItem("theoryfiles", filePaths)}
          resolve(filePaths);
        });
      });
    } 
    
    else {
      const options = {
        title: `Open ${filetag} files`,
        filters: [
          { name: `${filetag} files`, extensions: filetype.split(", ") },
          { name: "All files", extensions: ["*"] }
        ],
        properties: ["openFile", "multiSelections"],
        message: `Open ${filetag} files` //For macOS
      };
      electron.remote.dialog.showOpenDialog(null, options, filePaths => {
        if (filePaths == undefined) return console.log("No files selected");
        currentLocation = path.dirname(filePaths[0]);
        folderFile = updateFolder(currentLocation);
        localStorage.setItem(`${filetag}_location`, currentLocation)
        console.log(`[${filetag}]: location is stored locally\n${currentLocation}`)
      });
    }

  }
  
  $: delta_thz = 1
  $: gamma_thz = 0
  let fileInfo = {

    // Create baseline matplotlib

    felix:{
      pyfile:"baseline.py",
      args:[]
    },

    // Masspec matplotlib

    mass:{
      pyfile:"mass.py",
      args:"plot"
    },

    // Timescan matplotlib

    scan:{
      pyfile:"timescan.py",
      args:"plot"
    },

    // THz scan matplotlib

    thz:{

      pyfile:"thz_scan.py",
      // args:[delta_thz, "plot", gamma_thz] // Doesn't take the binded delta_thz value
      
    }
  }
  $: modal = {mass:"", felix:"", scan:"", thz:""}
  $: error_msg = {mass:"", felix:"", scan:"", thz:""}

  function functionRun(event, target_id=null) {
    let btname;

    target_id === null ? btname = event.target.id : btname = target_id

    console.log(`Button clicked (id): ${btname}`)
    if (btname === "createBaselineBtn"){btname="felix_Matplotlib"}
    let output_filename = document.getElementById("avg_output_name").value
    
    switch (btname) {

      ////////////// FELIX PLOT //////////////////////

      case "felixPlotBtn":

        jq("#theoryRow").css("display", "none")
        plotContainerHeight = "60vh"
        Plotly.purge("exp-theory-plot");

        runPlot({
          fullfiles: fullfiles, filetype: filetag, btname: btname,
          pyfile: "normline.py", normethod: normMethod, args: [delta, output_filename]
        })
        .then((output)=>{
          console.log(output)
          expfitDiv = "block"
        })
        .catch((err)=>{
          console.log('Error Occured', err); 
          error_msg[filetag]=err; 
          modal[filetag]="is-active"
        })
      
      break;


      case "exp_fit":

        let expfit_overwrite = document.getElementById("overwrite_expfit").checked
        console.log("Expfit overwrite: ", expfit_overwrite)
        console.log(`Avgplot Index: ${window.index}`)

        if (window.index.length > 0) {
          runPlot({
          fullfiles: fullfiles, filetype: "exp_fit", btname: btname,
          pyfile: "exp_gauss_fit.py", args: [expfit_overwrite, output_filename, normMethod, currentLocation, ...window.index]
          })
          .then((output)=>{
            console.log(output)
          })

          .catch((err)=>{
            console.log('Error Occured', err); 
            error_msg[filetag]=err; 
            modal[filetag]="is-active"
          })
        } 
        
      break;

      // Norm_tkplot (Averaged plot experimental in Matplotlib)

      case "norm_tkplot":
        console.log("Running Norm_tkplot")
        let avgdata = document.getElementById("avgplot").data
        runPlot({
                fullfiles: fullfiles,
                filetype: "general",
                filetag: "felix",
                btname: "norm_tkplot",
                pyfile: "norm_tkplot.py",
                args: [normMethod]
              })
      break;
      
      ////////////// Matplotlib PLOT //////////////////////

      case `${filetag}_Matplotlib`:

        console.log("Opening Matplotlib in tkinter")

        let scriptname = fileInfo[filetag]["pyfile"]
        let options = {args:[...fullfiles, fileInfo[filetag]["args"]]}

        if (filetag === "thz") {fileInfo[filetag]["args"]=[delta_thz, "plot", gamma_thz]}

        let obj = {
            fullfiles: fullfiles,
            filetag:filetag,            
            filetype: "general",
            btname: event.target.id,
            pyfile: fileInfo[filetag]["pyfile"],
            args: fileInfo[filetag]["args"]
          }
        runPlot(obj).then((output)=>console.log(output))
        .catch((err)=>{
          console.log('Error Occured', err); 
          error_msg[filetag]=err; 
          modal[filetag]="is-active"
        })

      break;

      ////////////// Masspec PLOT //////////////////////

      case "massPlotBtn":
          runPlot({
            fullfiles: fullfiles,
            filetype: filetag,
            btname: btname,
            pyfile: "mass.py",
            args: "run"
          })
          .then((output)=>{
            console.log(output)
          })
          .catch((err)=>{
            console.log('Error Occured', err); 
            error_msg[filetag]=err; 
            modal[filetag]="is-active"
          })
      break;

      ////////////// Timescan PLOT //////////////////////

      case "timescanBtn":
          fileChecked.forEach(file => {
              runPlot({
                fullfiles: join(file),
                filetype: filetag,
                btname: btname,
                pyfile: "timescan.py",
                plotArea: file + "_tplot"
              })
              .then((output)=>{
                console.log(output)
              })
              
              .catch((err)=>{
                console.log('Error Occured', err); 
                error_msg[filetag]=err; 
                modal[filetag]="is-active"
              })
            });
      break;

      ////////////// THz PLOT //////////////////////

      case "thzBtn":
           runPlot({
            fullfiles: fullfiles,
            filetype: filetag,
            btname: btname,
            pyfile: "thz_scan.py",
            args: [delta_thz, "run", gamma_thz]
          })
          .then((output)=>{
            console.log(output)
          })
          
          .catch((err)=>{
            console.log('Error Occured', err); 
            error_msg[filetag]=err; 
            modal[filetag]="is-active"
          })
      break;


      ////////////// Toggle buttons //////////////////////

      case "theoryBtn": 
        jq("#theoryRow").toggle()
        if (document.getElementById("theoryRow").style.display === "none") {plotContainerHeight = "60vh"} 
        else {plotContainerHeight = "50vh"}
      break;

      case "depletionscanBtn":
        jq("#depletionRow").toggle()
        if (document.getElementById("depletionRow").style.display === "none") {plotContainerHeight = "60vh"} 
        else {plotContainerHeight = "50vh"}
      break;

      ////////////////////////////////////////////////////
    
      default:
        break;

      //////////////////////////////////////////////////// 
    }
  };

  function opentheory() {
    browseFile({theory:true}).then(file =>  theoryfiles = file).catch(err => console.log(err));
  }

  function runtheory({tkplot="run", filetype="theory"}) {
    runPlot({
      fullfiles: theoryfiles, filetype: filetype, filetag:filetag,
      btname: "appendTheory", pyfile: "theory.py", args: [normMethod, sigma, scale, currentLocation, tkplot]
    }).then((output)=>{console.log(output)})
    .catch((err)=>{
        console.log('Error Occured', err); 

        error_msg[filetag]=err; 
        modal[filetag]="is-active"
      })
  }

  let sigma=20; //Sigma value for felixplot thoery gaussian profile
  let scale=1;

  let powerinfo = "21, 21";
  let nshots = 10;
  let massIndex = 0;
  let timestartIndex = 1;

  let depletionLabels = [
    {
      name: "Power (ON, OFF)",
      id: "powerinfo"
    },
    {
      name: "FELIX Hz",
      id: "nshots"
    },
    {
      name: "Mass Index",
      id: "massIndex"
    },
    {
      name: "TimeStart Index",
      id: "timeIndex"
    }
  ]

  const depletionPlot = () => {

    runPlot({fullfiles: [currentLocation], filetype: "depletion",
      btname: "depletionSubmit", pyfile: "depletionscan.py", 
      args: [jq(ResON).val(), jq(ResOFF).val(), powerinfo, nshots, massIndex, timestartIndex] })
      .then((output)=>{
        console.log(output)
      })
      .catch((err)=>{
        console.log('Error Occured', err); 
        error_msg["scan"]=err; 
        modal["scan"]="is-active"
      })
  }
  
  let output_filename =  "averaged";

  // Experimental fit (gaussian)

  // Fit one peak
  $: expfitDiv = "none"

  // Finding peak
  
  $: prominence = 5
  $: peak_width = 5
  $: peak_height = 0

  $: findPeak_btnCSS = "is-link"
  $: clear_all_Peak_btnCSS = "is-danger"
  $: clear_last_Peak_btnCSS = "is-warning"
  $: fitallPeak_btnCSS = "is-link"

  // Toggle find all peaks row
  $: exp_fitall_div_status = false
  $: exp_fitall_div = "none"
  $: exp_fitall_div_status ? exp_fitall_div = "block" : exp_fitall_div = "none"

  $: fit_files = "averaged"
  $: fit_file_list_temp = fileChecked.map(file => file.split(".")[0])
  $: fit_file_list = [...fit_file_list_temp, "averaged"]
  $: fitall_tkplot_Peak_btnCSS = "is-link"
  let ready_to_fit = false

  function expfit_func({runfit = false, btname = "find_expfit_peaks", tkplot=false} = {}) {

    let output_filename = document.getElementById("avg_output_name").value
    let expfit_overwrite = document.getElementById("overwrite_expfit").checked
    runPlot({
      fullfiles: [fit_files],
      filetype: "expfit_all",
      btname: btname,
      pyfile: "fit_all.py",
      args: [currentLocation, normMethod, prominence, runfit, peak_width, peak_height, expfit_overwrite, tkplot]
    })
    .then((output)=>console.log(output))
    .catch((err)=>{
      console.log('Error Occured', err); 
      error_msg[filetag]=err; 
      modal[filetag]="is-active"
    })
  }

  const findPeak = () => {
    console.log("Finding preak with prominence value: ", prominence)
    ready_to_fit = true
    expfit_func()
  }

  const clearAllPeak = () => {

    console.log("Removing all found peak values")

    window.annotations = []
    window.index = []

    Plotly.relayout("avgplot", { annotations: [], shapes: [] })
    let plottedFiles_length = window.line.length / 2
    console.log(`Total files plotted: ${plottedFiles_length}`)
    for (let i=0; i<plottedFiles_length; i++) {Plotly.deleteTraces("avgplot", [-1])}
    window.line = []

    ready_to_fit = false
  }

  const clearLastPeak = () => {

    console.log("Removing only last found peak values")
    if (window.line.length != 0) {Plotly.deleteTraces("avgplot", [-1])}
    
    window.line = window.line.slice(0, window.line.length - 2)
    window.annotations = window.annotations.slice(0, window.annotations.length - 1)

    window.index = []

    Plotly.relayout("avgplot", { annotations: window.annotations, shapes: window.line })

    if (window.line.length === 0) {ready_to_fit = false}
    
  }

  const fitall = (tkplot=false, btname="fitall_expfit_peaks") => {

    console.log("Fitting all found peaks")

    if (ready_to_fit) {expfit_func({runfit:true, btname:btname, tkplot:tkplot})}

    else {
      findPeak_btnCSS = "is-link shake"
      setTimeout(()=>findPeak_btnCSS = "is-link", 1000)
    }
  }

</script>

<style>

  input[type="number"] {width: 5vw;}
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
    width: 70%;
    position: absolute;
  }

  .data-loading {
    display: none;
  }

  #theoryContainer {
    margin-left: 20%;
    margin-right:20%;
  }
</style>

<section class="section" {id} {style}>

  <div class="columns">

    <div class="column is-3 filebrowserColumn" id="{filetag}filebrowserColumn">
      <Filebrowser
        {filetag} {currentLocation} {updateFolder}
        {getCheckedFiles} {jq} {path} />
    </div>

    <div class="column">

      <div class="modal {modal[filetag]} is-clipped">
        <div class="modal-background"></div>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">Error Occured while processing the data</p>
            <button class="delete" aria-label="close" on:click="{()=>modal[filetag]=''}"></button>
          </header>
          <section class="modal-card-body" style="color:black"> {error_msg[filetag]} </section>

          <footer class="modal-card-foot">
            <button class="button" on:click="{()=>modal[filetag]=''}">Close</button>
          </footer>
        </div>
      </div>

      <div class="row locationRow">

        <div class="field has-addons">
          <div class="control is-expanded">
            <input
              class="input locationLabel"
              type="text"
              placeholder="Location will be displayed"
              id="{filetag}LocationLabel"
              value={currentLocation} 
              on:keyup="{
                (e)=>{
                  if (e.key == "Enter") {
                    let location = e.target.value
                    console.log(`Setting location: ${location}`)
                    currentLocation = location
                  }
                }
              }" 
              data-tippy="Current Location"/>
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

      <div class="row buttonsRow">

        <div class="level">

          <div class="level-left animated fadeIn">

            {#each funcBtns as { id, name }}
              <div 
                class="level-item button hvr-glow funcBtn is-link animated"
                {id} on:click={functionRun}>
                {name}
              </div>

            {/each}

            {#each checkBtns as {id, name, bind, help}}
               <div class="level-item animated" id="{id}_Container" >

                <div class="pretty p-default p-curve p-toggle" data-tippy={help}>

                  {#if name[0]==="Log"}
                    <input type="checkbox" {id} checked={bind} on:click={linearlogCheck} />
                  {:else}
                    <input type="checkbox" {id} checked={bind} on:click="{(e)=>{console.log(`Status (${e.target.id}):\n ${e.target.checked}`)}}"/>
                  {/if}

                  <div class="state p-success p-on"> <label>{name[0]}</label> </div>
                  <div class="state p-danger p-off"> <label>{name[1]}</label> </div>

                </div>
                
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
                        {#each normalisation_method as method}
                           <option>{method}</option>
                        {/each}
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
                      on:change="{(e)=>functionRun(e, "felixPlotBtn")}" />
                  </div>
                </div>
              </div>
            {/if}

            {#if filetag == 'thz'}

              <!-- Delta value -->
              <div class="level-item" >

                <div class="field has-addons">
                  <div class="control"><div class="button is-static">&delta; (in Hz)</div></div>

                  <div class="control">
                    <input
                      class="input"
                      type="number" step="0.5"
                      id="delta_value_thz"
                      placeholder="Delta value"
                      data-tippy="Delta value for spectrum (in KHz)"
                      bind:value={delta_thz}
                      on:change="{(e)=>functionRun(e, "thzBtn")}" />
                  </div>
                  
                </div>

              </div>

              <!-- Gamma -->

              <div class="level-item">

                <div class="field has-addons">
                  <div class="control"><div class="button is-static">&gamma;</div></div>

                  <div class="control">
                    <input
                      class="input"
                      type="number" step="0.01"
                      id="gamma_thz"
                      placeholder="Gamma value for lorentz part"
                      data-tippy="Lorentz gamma for fitting (Voigt Profile)"
                      bind:value={gamma_thz}
                      on:change="{(e)=>functionRun(e, "thzBtn")}"/>
                  </div>
                  
                </div>

              </div>

            {/if}
          </div>
        </div>

      </div>

      {#if filetag=="felix"}
         <div class="row" id="theoryRow" style="display:none; padding-bottom:1em">
            <div class="container is-marginless" id="theoryContainer">
              <div class="field">
                <label class="label" id="theorylabel">
                  <h1 class="subtitle" id="theoryfilename">{theoryfilenames}</h1>
                </label>
                <div class="control">
                    <button class="button is-warning" on:click={opentheory}>Choose file</button>
                    <input class="input" type="number" on:change="{()=>runtheory({tkplot:"run"})}" bind:value={sigma} style="width:150px" data-tippy="Sigma (deviation) from central frequency">
                    <input class="input" type="number" on:change="{()=>runtheory({tkplot:"run"})}" step="0.001" bind:value={scale} style="width:150px" data-tippy="Scaling factor (to shift in position)">
                    <button class="funcBtn button is-link animated" on:click={runtheory} id="appendTheory">Submit</button>
                    <button class="funcBtn button is-link animated" on:click="{()=>runtheory({tkplot:"plot", filetype:"general"})}" id="theory_Matplotlib">Open in Matplotlib</button>
                </div>
              </div>
            </div>
         </div>
      {/if}

      {#if filetag=="scan"}
         <div class="row" id="depletionRow" style="display:none">
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

                {#each depletionLabels as {name, id}}
                  <div class="level-item">
                    <div class="field">
                      <label class="label"><h1 class="subtitle">{name}</h1></label>
                      <div class="control">
                      {#if name=="Power (ON, OFF)"}
                        <input class="input" type="text" bind:value={powerinfo} {id}>
                      {:else if  name=="FELIX Hz"}
                        <input class="input" type="number" bind:value={nshots} {id}>
                      {:else if  name=="Mass Index"}
                        <input class="input" type="number" bind:value={massIndex} {id}>
                      {:else if  name=="TimeStart Index"}
                        <input class="input" type="number" bind:value={timestartIndex} {id}>
                      {/if}
                          
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
      <!-- <h1 class="subtitle">Data Visualisation</h1> -->

      <div class="row box plotContainer" style="max-height: {plotContainerHeight};" id="{filetag}plotMainContainer" >
        
        <div class="container is-fluid" id="{filetag}plotContainer">
          {#each plotID as id}
            {#if filetag == 'scan'}
              <div {id} style="padding-bottom:1em">
                {#each fileChecked as scanfile}
                  <div id="{scanfile}_tplot" style="padding-bottom:1em" />
                {/each}
              </div>

            {:else if id == 'avgplot'}

              <div {id} style="padding-bottom:1em" />

              <div class="level" style="display:{exp_fitall_div}">
                <div class="level-left">

                  <div class="level-item">
                      <input class="input" type="number" id="peak_prominance" placeholder="Peak prominance value"
                        data-tippy="Peak prominace value" bind:value={prominence} on:change={expfit_func} min="0"/>
                  </div>

                  <div class="level-item">
                      <input class="input" type="number" id="peak_width_fit" placeholder="Peak width"
                        data-tippy="Optional: Peak width" bind:value={peak_width} on:change={expfit_func} min="0"/>
                  </div>

                  <div class="level-item">
                      <input class="input" type="number" id="peak_height_fit" placeholder="Peak height"
                        data-tippy="Optional: Peak height" bind:value={peak_height} on:change={expfit_func} min="0"/>
                  </div>

                  <div class="level-item">
                      <div class="level-item button hvr-glow funcBtn animated {findPeak_btnCSS}"
                        id="find_expfit_peaks" on:click={findPeak} data-tippy="Find the peaks by adjusting the prominence value">Get Peaks
                      </div>
                  </div>

                  <div class="level-item">
                    <div class="select">
                      <select id="fitFiles" bind:value={fit_files}>
                          {#each fit_file_list as file}
                            <option>{file}</option>
                          {/each}
                        </select>
                    </div>
                      
                  </div>

                  <div class="level-item">
                      <div class="level-item button hvr-glow funcBtn animated {fitallPeak_btnCSS}"
                        id="fitall_expfit_peaks" data-tippy="Fit all the peaks positions found using gaussian" on:click={fitall}>Fit
                      </div>
                  </div>

                  <div class="level-item">
                      <div class="level-item button hvr-glow funcBtn animated {fitall_tkplot_Peak_btnCSS}"
                        id="fitall_tkplot_expfit_peaks" data-tippy="Fit all the peaks positions found using gaussian" on:click="{()=>fitall(true, 'fitall_tkplot_expfit_peaks')}">Open in Matplotlib
                      </div>
                  </div>

                </div>
              </div>

              <div class="level" style="display:{expfitDiv}">
                <div class="level-left">

                  <div class="level-item">
                    <input class="input" type="text" id="avg_output_name" placeholder="Averaged spectra output filename"
                      data-tippy="Averaged spectra output filename" bind:value={output_filename} disabled />
                  </div>

                  <div class="level-item">
                    <div class="level-item button hvr-glow funcBtn is-link animated"
                      id="exp_fit" on:click={functionRun}>Exp. Fit
                    </div>
                  </div>

                  <div class="level-item">
                    <div class="pretty p-switch p-slim" style="margin-left:1em;" data-tippy="Overwrite existing expfit file with only new values ? or else will append to existing file">
                        <input type="checkbox" id="overwrite_expfit"/>
                        <div class="state p-info p-on">
                            <label>Overwrite</label>
                        </div>
                    </div>
                  </div>

                  <div class="level-item">
                      <div class="level-item button hvr-glow funcBtn animated {clear_last_Peak_btnCSS}"
                        id="clearLast_plotted_peaks" on:click={clearLastPeak} data-tippy="Clear last fitted lines">Clear last
                      </div>
                  </div>

                  <div class="level-item">
                      <div class="level-item button hvr-glow funcBtn animated {clear_all_Peak_btnCSS}"
                        id="clearAll_plotted_peaks" on:click={clearAllPeak} data-tippy="Clear all fitted lines">Clear all
                      </div>
                  </div>

                  <div class="level-item">
                      <div class="level-item button hvr-glow funcBtn is-link animated"
                        id="findall_expfit_toggle" on:click="{()=>exp_fitall_div_status = !exp_fitall_div_status}">Find Peaks
                      </div>
                  </div>
                </div>
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
