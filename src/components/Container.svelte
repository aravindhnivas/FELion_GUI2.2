<script>

  import Filebrowser from "./utils/Filebrowser.svelte";
  import { runPlot } from "./utils/js/felion_main.js";
  import * as dirTree from "directory-tree";
  import { fade, fly } from 'svelte/transition';
  // import { spawn, exec } from "child_process";

  const glob = require("glob")

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

  jq(document).ready(() => {

    jq("#theoryBtn").addClass("fadeInUp").css("display", "none")
    jq("#norm_tkplot").addClass("fadeInUp").css("display", "none")

    jq("#exp_fit").addClass("fadeInUp").css("display", "none")
    jq("#felix_shell_Container").addClass("fadeInUp").css("display", "block")

    let plotHeight;
    let ScreenHeight = window.screen.height;

    if (ScreenHeight >= 1000) plotHeight = 650
    else plotHeight = 540

    jq(".plotContainer").css("max-height", plotHeight)

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

  const locationUpdateStatus = (status) => {
    jq(document).ready(()=>{
      
      let locationUpdateDiv = document.getElementById(`${filetag}locationUpdate`)

      locationUpdateDiv.innerHTML = status
      locationUpdateDiv.style.display = "block"
      
      setTimeout(()=>{
        locationUpdateDiv.innerHTML=""
        locationUpdateDiv.style.display = "none"
      }, 2000)
      
    })
  }

  const updateFolder = location => {

    console.log("Folder updating");
    locationUpdateStatus("Folder updating...")

    if (location === undefined || location === 'undefined') {
      console.log("Location is undefined");
      jq(`#${filetag}refreshIcon`).removeClass("fa-spin");
      locationUpdateStatus("Location undefined!")
      return undefined;
    } 

    currentLocation = location;
    localStorage.setItem(`${filetag}_location`, currentLocation)
    jq(`#${filetag}refreshIcon`).addClass("fa-spin");
    console.log(`[${filetag}]: location is stored locally\n${currentLocation}`)

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
      locationUpdateStatus("Folder updated")

    } catch (err) {
      console.log(`Error Occured: ${err}`)
      locationUpdateStatus("Error Occured:")
    }

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
    
    switch (btname) {

      ////////////// FELIX PLOT //////////////////////

      case "felixPlotBtn":

        jq("#theoryRow").css("display", "none")
        // plotContainerHeight = "60vh"
        Plotly.purge("exp-theory-plot");

        runPlot({
          fullfiles: fullfiles, filetype: filetag, btname: btname,
          pyfile: "normline.py", normethod: normMethod, args: [delta, fit_files]
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
        let fitfile = document.getElementById("expfitFiles").value

        console.log("Expfit overwrite: ", expfit_overwrite)
        console.log(`Avgplot Index: ${window.index}`)

        if (window.index.length > 0) {
          runPlot({
          fullfiles: fullfiles, filetype: "exp_fit", btname: btname,
          pyfile: "exp_gauss_fit.py", args: [expfit_overwrite, fitfile, normMethod, currentLocation, ...window.index]
          })
          .then((output)=>{
            console.log(output)
          })

          .catch((err)=>{
            console.log('Error Occured', err); 
            error_msg[filetag]=err; 
            modal[filetag]="is-active"
          })
        } else {expfit_log_it("Please select a range from Averaged Spectrum")}
        
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
          // show_nist = false

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

      case "mass_find_peaks":
        console.log("Finding mass peaks")
        jq("#mass_peak_find_row").toggle()

      break;

      case "nist_webbook":
        
        jq("#nist_row").toggle()
        jq("#nistWebview_rows").toggle()

        checkInternet().then(result=>{
          internet_connection = result
          internet_active = "is-success"
        }).catch(err=>{
          internet_connection = result
          internet_active = "is-danger"
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

      case "theoryBtn": 
        jq("#theoryRow").toggle()

      break;

      case "depletionscanBtn":
        jq("#depletionRow").toggle()
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
      name: "MassIndex",
      id: "massIndex"
    },
    {
      name: "TimeStart",
      id: "timeIndex"
    }
  ]
  const depletionPlot = async () => {
    runPlot({
      fullfiles: [currentLocation], filetype: "general", filetag:"scan",
      btname: "depletionSubmit", pyfile: "depletionscan.py", 
      args: [jq(ResON).val(), jq(ResOFF).val(), ...powerinfo.split(",").map(pow=>parseFloat(pow)), nshots, massIndex, timestartIndex] 
    })
    .then((output)=>{console.log(output)})
    .catch((err)=>{
      console.log('Error Occured', err); 
      error_msg["scan"]=err; 
      modal["scan"]="is-active"
    })

  /* Streamlit depletion */
  // let port = 8501
    // let pyFile = path.resolve(__dirname, "python_files", "depletion_streamlit.py")
    // let pyDir = path.dirname(localStorage["pythonpath"])
    // let streamlit_path = path.resolve(pyDir, "Scripts", "streamlit")

    // glob(path.resolve(pyDir, "Scripts", "streamlit*"), (error, file)=>{
    //   if(file.length===0){
    //     console.log("Error: Streamlit is not installed.\nInstalling now...")
    //     let packageName = "streamlit-0.51.0-py2.py3-none-any.whl"
    //     let streamlit_package = path.resolve(__dirname, "pipPackages", packageName)
    //     exec(`${path.resolve(pyDir, "python")} -m pip install ${streamlit_package}`, (err, result)=>{
    //       if (err) {console.log("Error occured: Streamlit package couldn't be installed to python")}
    //       else {console.log("Streamlit package installed to python: \n", result)}
    //     })
    //   } else {console.log("Streamlit exists")}
    // })

    // let defaultArguments = ["run", pyFile, "--server.port", port, "--server.headless", "true"]
    // let sendArguments = [currentLocation, ...folderFile.files]

    // let st = spawn(streamlit_path, [...defaultArguments, ...sendArguments])
    // st.stdout.on('data', data => {console.log(data.toString("utf8"))})
    // st.stderr.on('data', err => {console.log("Error occured:", err.toString("utf8"))})
    // st.on('close', ()=>{console.log("Completed")})

    // let localhostDepletion = `http://localhost:${port}`
    // setTimeout(()=>window.open(localhostDepletion), 1000)
  }

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
  $: fit_file_list = ["averaged", ...fit_file_list_temp]

  $: fitall_tkplot_Peak_btnCSS = "is-link"

  // expfit clear and clear all status
  $: expfit_log_display = false
  $: expfit_log = ""
  const expfit_log_it = (str) => {
    
    expfit_log_display = true
    expfit_log = str
    
    setTimeout(()=>{
      expfit_log_display = false
    }, 4000)
  }

  let ready_to_fit = false

  function expfit_func({runfit = false, btname = "find_expfit_peaks", tkplot=false, filetype="expfit_all"} = {}) {

    let expfit_overwrite = document.getElementById("overwrite_expfit").checked
    let fitfile = document.getElementById("fitFiles").value

    runPlot({
      fullfiles: [fitfile],
      filetype: filetype,
      filetag: filetag,
      btname: btname,
      pyfile: "fit_all.py",
      args: [currentLocation, normMethod, prominence, runfit, peak_width, peak_height, expfit_overwrite, tkplot, ...fullfiles]
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

  const delete_file_line = ({btname = "exp_fit"} = {}) => {
    let fitfile = document.getElementById("expfitFiles").value
    runPlot({
      fullfiles: [fitfile],
      filetype: "general",
      filetag: filetag,
      btname: btname,
      pyfile: "delete_fileLines.py",
      args: [currentLocation]
    })
    .then((output)=>console.log(output))
    .catch((err)=>{
      console.log('Error Occured', err); 
      error_msg[filetag]=err; 
      modal[filetag]="is-active"
    })
  }
  const clearAllPeak = () => {
    console.log("Removing all found peak values")
    let lines_length = window.line.length
    let annotations_length = window.annotations.length
    if (lines_length === 0 & annotations_length === 0) {expfit_log_it("No fitted lines found")}

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
    
    if (window.line.length > 0) {
      delete_file_line()
      Plotly.deleteTraces("avgplot", [-1])

      console.log("Last fitted peak removed")
    } else {
      
      if (window.annotations.length === 0) {expfit_log_it("No fitted lines found")}
      console.log("No line fit is found to remove")
    }
    
    window.line = window.line.slice(0, window.line.length - 2)
    window.annotations = window.annotations.slice(0, window.annotations.length - 1)
    window.index = []
    Plotly.relayout("avgplot", { annotations: window.annotations, shapes: window.line })
    if (window.line.length === 0) {ready_to_fit = false}
  }


  const fitall = (tkplot=false, btname="fitall_expfit_peaks", filetype="expfit_all") => {

    console.log("Fitting all found peaks")
    if (ready_to_fit) {expfit_func({runfit:true, btname:btname, tkplot:tkplot, filetype:filetype})}

    else {
      findPeak_btnCSS = "is-link shake"
      setTimeout(()=>findPeak_btnCSS = "is-link", 1000)
    }
  }

  $: mass_peak_width = 2
  $: mass_prominence = 3
  $: mass_peak_height = 40
  
  const find_masspec_peaks = () => {

    console.log("Finding masspec peaks")

    let sendMassFile = path.join(currentLocation, massFiles.value)

    runPlot({
      fullfiles: [sendMassFile],
      filetype: "find_peaks",
      filetag: filetag,
      btname: "mass_get_peaks",
      pyfile: "find_peaks_masspec.py",
      args: [mass_prominence, mass_peak_width, mass_peak_height]
    })
    .then((output)=>console.log(output))
    .catch((err)=>{
      console.log('Error Occured', err); 
      error_msg[filetag]=err; 
      modal[filetag]="is-active"
    })
  }

  const clear_mass_peaks = () => {Plotly.relayout("mplot", { annotations: [] })}

  $: nist_mformula = localStorage["nist_mformula"] || ""
  $: nist_mname = localStorage["nist_mname"] || ""
  $: nist_molecule_name = `Name=${nist_mname}`
  $: nist_molecule_formula = `Formula=${nist_mformula}`
  $: nist_url = localStorage["nist_url"] || "https://webbook.nist.gov/cgi/cbook.cgi?Name=&Units=SI&Mask=200#Mass-Spec"


  const set_nist_url = (format) => {

    let fmt;
    format == "by_name" ? fmt = nist_molecule_name : fmt = nist_molecule_formula
    nist_url = `https://webbook.nist.gov/cgi/cbook.cgi?${fmt}&Units=SI&Mask=200#Mass-Spec`

    localStorage["nist_url"] = nist_url
    localStorage["nist_mformula"] =  nist_mformula
    localStorage["nist_mname"] = nist_mname
  }

  function checkInternet() {

    return new Promise((resolve, reject)=>{
      require('dns').lookup('google.com',function(err) {
          if (err && err.code == "ENOTFOUND") {
              reject("No Internet access available")
          } else {
              resolve("Internet Connected")
          }
      })
    })
  }

  $: internet_connection = "No Internet access available"
  $: internet_active = "is-danger"
  $: search_string = ""
  $: google_search = `http://www.google.com/search?q=${search_string}.`


  function animatePlot(){
    try {
      let data = window.avg_data[normMethod]["data"]
      let layout = window.avg_data[normMethod]["layout"]
      Plotly.react("avgplot", data , layout )
    } catch (err) {console.log("Error occured while chaning felixplot method", err)}
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
    padding-bottom: 0.6em;
  }

  .funcBtn {
    margin: 0 0.5em;
  }
  .section {
    position: fixed;
    width: 100%;
    padding: 0.3rem;
  }
  .plotContainer {
    overflow-y: auto;
    width: 97%;
  }

  /* Buttons:  border, background and hovering colors */
  .button.is-link, .button.is-warning, .button.is-danger {background-color: rgba(0,0,0,0);}

  .button.is-link {border-color: #dbdbdb;}
  .button.is-link:hover, .button.is-link.is-hovered {background-color: #7a64b1;}

  .button.is-warning {border-color: #ffc402; color: white;}
  .button.is-warning:hover, .button.is-warning.is-hovered {background-color: #7a64b1; color: white;}

  .button.is-danger {border-color: #ff3860;}
  .button.is-danger:hover, .button.is-danger.is-hovered {background-color: #ff3860;}

  .button.is-static {background: transparent; color: white;}

  /*  */

  /* Input hover, focused colors */
  .input {
    background: transparent;
    color: white;
  }

  .locationLabel {border-radius: 20px;}

  .input:hover {border-color: #fafafa;}
  .input:focus {
    border-color: #fafafa;
    box-shadow: 0 0 0 0.05em #fafafa;
  }
  .column {max-height: 90vh}
  .delete:hover {background-color:#ff3860}

  .filebrowserColumn {width: 14%!important}

  @media only screen
  and (max-width: 1400px) {
    .filebrowserColumn {width: 20%!important}
  }

  #nist_webview {height:42em;}
  .webviewIcon {cursor: pointer;}
  .level-item {margin-left: 0!important}

  .locationRow {margin-right: 2em;}
  .row1 {
    margin: 0;
    background-color: #594194;
    margin-right: 2em;
  }
  .subtitle {color: #fafafa;}

</style>

<section class="section" {id} {style}>

  <div class="columns">

    <div class="column is-2 filebrowserColumn" id="{filetag}filebrowserColumn">
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

      <div class="row row1 box">
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
              <div class="button is-link" on:click={browseFile}>Browse</div>
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
                <!-- <div class="level-item">
                  <span class="select">
                    <select
                      id="felixmethod"
                      bind:value={normMethod}
                      data-tippy="Normalisation method"
                      on:change={animatePlot}>
                      {#each normalisation_method as method}
                        <option>{method}</option>
                      {/each}
                    </select>
                  </span>
                </div> -->
                <div class="level-item">
                  <div class="field has-addons">
                    <div class="control"><div class="button is-static">&Delta (cm-1)</div></div>

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
              <div class="level " id="theoryContainer">
                  <div class="level-left">

                    <div class="level-item">
                      <div class="control">
                        <div class="select">
                          <select>
                              {#each theoryfilenames as theoryfile}
                                  <option value={theoryfile}>{theoryfile}</option>
                              {/each}
                          </select>
                        </div>
                      </div>
                    </div>

                    <div class="level-item">
                      <div class="control">
                          <button class="button is-link" on:click={opentheory}>Choose file</button>
                          <input class="input" type="number" on:change="{()=>runtheory({tkplot:"run"})}" bind:value={sigma} style="width:150px" data-tippy="Sigma (deviation) from central frequency">
                          <input class="input" type="number" on:change="{()=>runtheory({tkplot:"run"})}" step="0.001" bind:value={scale} style="width:150px" data-tippy="Scaling factor (to shift in position)">
                          <button class="funcBtn button is-link animated" on:click={runtheory} id="appendTheory">Submit</button>
                          <button class="funcBtn button is-link animated" on:click="{()=>runtheory({tkplot:"plot", filetype:"general"})}" id="theory_Matplotlib">Open in Matplotlib</button>
                      </div>
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
                          {:else if  name=="MassIndex"}
                            <input class="input" type="number" bind:value={massIndex} {id}>
                          {:else if  name=="TimeStart"}
                            <input class="input" type="number" bind:value={timestartIndex} {id}>
                          {/if}
                        </div>
                      </div>

                    </div>
                  {/each}

                  <div class="level-item" style="margin-top:2em">
                    <button class="funcBtn button animated is-link" id="depletionSubmit" on:click={depletionPlot}>Submit</button>
                  </div>

                </div>
              </div>

              
          </div>
        {/if}

        {#if filetag === "mass"}

          <!-- NIST find molecule row -->
          <div class="row" id="nist_row" style="display:none">
            <div class="level">
              <div class="level-left">

                <div class="level-item">
                  <input class="input" type="text" placeholder="Molecule name" 
                  data-tippy="Enter molecule name" bind:value={nist_mname} on:change="{()=>set_nist_url("by_name")}"/>
                </div>

                <div class="level-item">
                  <input class="input" type="text" placeholder="Molecule Formula" 
                  data-tippy="Enter molecule formula" bind:value={nist_mformula} on:change="{()=>set_nist_url("by_formula")}"/>
                </div>

                <div class="level-item">
                  <button class="button {internet_active}">{internet_connection}</button>
                </div>

              </div>
            </div>
          </div>

          <!-- Find mass peaks row -->
          <div class="row" id="mass_peak_find_row" style="display:block; padding-bottom:1em;">
            <div class="level">
              <div class="level-left">

                <div class="level-item">
                  <div class="select">
                    <select id="massFiles">
                        {#each fileChecked as file}
                          <option>{file}</option>
                        {/each}
                      </select>
                  </div>
                </div>

                  <div class="level-item">
                      <input class="input" type="number" placeholder="Peak prominance value"
                        data-tippy="Peak prominace value" bind:value={mass_prominence} on:change={find_masspec_peaks} min="0" step="0.5"/>
                  </div>

                  <div class="level-item">
                      <input class="input" type="number" placeholder="Peak width"
                        data-tippy="Optional: Peak width" bind:value={mass_peak_width} on:change={find_masspec_peaks} min="0" step="0.5"/>
                  </div>

                  <div class="level-item">
                      <input class="input" type="number" placeholder="Peak Height"
                        data-tippy="Optional: Peak Height" bind:value={mass_peak_height} on:change={find_masspec_peaks} min="0" step="0.5"/>
                  </div>

                  <div class="level-item">
                      <div class="level-item button is-link hvr-glow funcBtn animated"
                        id="mass_get_peaks" on:click={find_masspec_peaks} >Get Peaks
                      </div>
                  </div>

                  <div class="level-item">
                      <div class="level-item button is-danger hvr-glow funcBtn animated"
                        id="mass_clear_peaks" on:click={clear_mass_peaks} data-tippy="Clear all peaks">Clear
                      </div>
                  </div>
              </div>
            </div>
          </div>

        {/if}

      </div>

      <div class="row box plotContainer" id="{filetag}plotMainContainer" >
        
        <div class="container is-fluid" id="{filetag}plotContainer">
          {#each plotID as id}

            {#if filetag == 'scan'}
              <div class="columns is-multiline" {id} style="padding-bottom:1em">
                {#each fileChecked as scanfile}
                  <div class="column is-half" id="{scanfile}_tplot" style="padding-bottom:1em" />
                {/each}
              </div>

            {:else if id == 'avgplot'}

              <!-- Normalisation Method -->
              <div class="level">
                <div class="level-left">

                    <!-- Relative -->
                    <div class="level-item">
                      <div class="pretty p-icon p-curve p-pulse">
                          <input type="radio" name="normMethod" bind:group={normMethod} value="Relative" on:change={animatePlot}>
                          <div class="state p-success">
                              <i class="icon mdi mdi-check"></i>
                              <label>Relative</label>
                          </div>
                      </div>
                    </div>

                    <!-- Log -->
                    <div class="level-item">
                      <div class="pretty p-icon p-curve p-pulse">
                          <input type="radio" name="normMethod" bind:group={normMethod} value="Log" on:change={animatePlot}>
                          <div class="state p-success">
                              <i class="icon mdi mdi-check"></i>
                              <label>Log</label>
                          </div>
                      </div>
                    </div>

                    <!-- Intensitity per photon -->
                    <div class="level-item">
                      <div class="pretty p-icon p-curve p-pulse">
                          <input type="radio" name="normMethod" bind:group={normMethod} value="IntensityPerPhoton" on:change={animatePlot}>
                          <div class="state p-success">
                              <i class="icon mdi mdi-check"></i>
                              <label>Inten. per photon</label>
                          </div>
                      </div>
                    </div>

                </div>
              </div>

              <!-- Avgplot -->
              <div {id} style="padding-bottom:1em" />

              <!-- Experimental gaussian fitting -->
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
                        id="fitall_tkplot_expfit_peaks" data-tippy="Fit all the peaks positions found using gaussian" on:click="{()=>fitall(true, 'fitall_tkplot_expfit_peaks', 'general')}">Open in Matplotlib
                      </div>
                  </div>

                </div>
              </div>

              <div class="level" style="display:{expfitDiv}">
                <div class="level-left">

                  <div class="level-item">
                    <div class="select">
                      <select id="expfitFiles" bind:value={fit_files}>
                          {#each fit_file_list as file}
                            <option>{file}</option>
                          {/each}
                        </select>
                    </div>
                  </div>

                  <div class="level-item">
                    <div class="level-item button hvr-glow funcBtn is-link animated"
                      id="exp_fit" on:click={functionRun} data-tippy="Choose the file from the dropdown --> Fit">Exp. Fit
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

                  {#if expfit_log_display}
                    <div class="level-item" in:fade out:fly="{{ y: 50, duration: 1000 }}" id="expfit_log_id">
                      <label class="label" style="font-weight:400">{expfit_log}</label>
                    </div>
                  {/if}
                </div>
              </div>
            
            {:else if filetag==="mass"}

              <!-- mplot row -->
              <div {id} style="padding-bottom:1em;" />
              
              <!-- NIST webview -->
              <div class="row" id="nistWebview_rows" style="display:none">

                <!-- NIST webview navigator -->
                <div class="row">
                  <div class="level">
                    <div class="level-left">

                      <div class="level-item webviewIcon hvr-glow" on:click="{()=>nist_webview.goToIndex(0)}">
                        <span class="icon"><i class="fas fa-home"></i></span>
                      </div>

                      <!-- <div class="level-item">
                        <input class="input" type="text" placeholder="Google Search engine" 
                        data-tippy="Google Search engine" bind:value={search_string} on:change="{()=>nist_url=google_search}"/>
                      </div> -->

                      <div class="level-item webviewIcon hvr-glow" on:click="{()=>{if(nist_webview.canGoBack()) {nist_webview.goBack()}}}">
                        <span class="icon"><i class="fas fa-arrow-left"></i></span>
                      </div>

                      <div class="level-item webviewIcon hvr-glow" on:click="{()=>{if(nist_webview.canGoForward()) {nist_webview.goForward()}}}">
                        <span class="icon"><i class="fas fa-arrow-right"></i></span>
                      </div>

                      <div class="level-item webviewIcon hvr-glow" on:click="{()=>nist_webview.reload()}">
                        <span class="icon"><i class="fas fa-undo"></i></span>
                      </div>
                      
                    </div>
                  </div>
                </div>
                
                <!-- NIST webview -->
                <div class="row"><webview src={nist_url} id="nist_webview"></webview></div>

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
