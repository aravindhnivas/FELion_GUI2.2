<script>

    export let jq;
    export let path;
    export let mainWindow;
    export let showinfo;


    // Importing modules
    const {exec} = require("child_process")
    const https = require('https');
    const fs = require('fs')
    const admZip = require('adm-zip');
    const copy = require('recursive-copy');

    // When DOMContentent is loaded and ready
    jq(document).ready(()=>{jq("#ConfigurationContainer").addClass("is-active")})

    // Reading local package.json file
    let packageJSON = fs.readFileSync(path.join(__dirname, "../package.json"))
    packageJSON = JSON.parse(packageJSON.toString("utf-8"))
    let currentVersion = packageJSON.version

    // Pythonpath and pythonscript files location
    if (!localStorage["pythonpath"]) localStorage["pythonpath"] = path.resolve(__dirname, "..", "python3.7", "python")
    if (!localStorage["pythonscript"]) localStorage["pythonscript"] = path.resolve(__dirname, "python_files")
    let pythonpath = localStorage["pythonpath"];
    let pythonscript = localStorage["pythonscript"];

    // Getting python version
    let pythonv;
    exec(`${pythonpath} -V`, (err, stdout, stderr)=>{pythonv = stdout})

    // Pages in Settings
    let items = ["Configuration", "Update", "About"]

    //////////////////////////////////////////////////// FUNCTIONS ////////////////////////////////////////////////////

    // Config save function

    const fadeInfadeOut = () => {

        saveChanges = "block"
        setTimeout(()=>saveChangeanimate="fadeOut", 1200)
        setTimeout(()=>{
            saveChangeanimate = "fadeIn"
            saveChanges = "none"
        }, 2000)
    }

    $: saveChanges = "none"
    $: saveChangeanimate = "fadeIn"

    const configSave = () => {

        localStorage["pythonpath"] = pythonpath
        localStorage["pythonscript"] = pythonscript
        console.log(`Updated: \nPythonpath: ${localStorage.pythonpath}\nPython script: ${localStorage.pythonscript}`)

        fadeInfadeOut()

    }

    // Page toggle function
    const toggle = (event) => {
        let target = event.target.id
        items.forEach(item=>{
            let elementID = `${item}Container`
            let $element = jq(`#${elementID}`)

            let targetElement = document.getElementById(item)

            if (elementID != target) {
                if($element.hasClass("is-active")) {
                    $element.removeClass("is-active")
                    targetElement.style.display = "none"
                }
            } else {

                $element.addClass("is-active")
                targetElement.style.display = "block"
            }
        })
    }

    $: new_version = ""
    $: updatetoggle = "none"
    $: checkupdateLoading = ""
    $: updateLoading = ""
    $: updateStatus = ""

    // Github details
    const github = {
        username: "aravindhnivas",
        repo: "FELion_GUI2.2",
        branch: "master",
    }

    // URL for github files and folders
    const urlPackageJson = `https://raw.githubusercontent.com/${github.username}/${github.repo}/${github.branch}/package.json`
    const urlzip = `https://codeload.github.com/${github.username}/${github.repo}/zip/${github.branch}`

    // Local update-downloaded files
    const updateFolder = path.resolve(__dirname, "..", "update")
    const updatefilename = "update.zip"
    const zipFile = path.resolve(updateFolder, updatefilename)

    // Update checking
    const updateCheck = () => {

        updatetoggle = "none"
        console.log("Checking for update")

        checkupdateLoading = "is-loading"
        let request = https.get(urlPackageJson, (res) => {

            console.log('statusCode:', res.statusCode);
            console.log('headers:', res.headers);

            res.on('data', (data) => {

                data = JSON.parse(data.toString("utf8"))
                new_version = data.version

                console.log(`Received package:`, data)
                console.log(`Version available ${new_version}`)
                console.log(`Current version ${localStorage.version}`)

                updatetoggle = "block"
                checkupdateLoading = "animated bounce is-success"
                setTimeout(()=>checkupdateLoading = "", 2000)
            })
            
            res.on("error", (err)=>{
                console.log("Error while reading downloaded data: ", err)
                new_version = ""
            });
        })
        
        request.on('error', (err) => {
            console.error("Error occured: (Try again or maybe check your internet connection)\n", err)
            checkupdateLoading = "animated shake faster is-danger"
            setTimeout(()=>checkupdateLoading = "", 2000)
            updateStatus = "Try again or Check your internet connection"
        });

        request.on("close", ()=>{
            if (currentVersion === new_version) {updateStatus = "No major new update available (Still you can update to see the latest minor updates if any available)"}
            else if (currentVersion < new_version) {

                updateStatus = "New update available"

                let options = {
                    title: "FELion_GUI2",
                    message: "Update available "+new_version,
                    buttons: ["Update and restart", "Later"],
                    type:"info"
                }
                
                let response = showinfo(mainWindow, options)
                console.log(response)
                switch (response) {
                    case 0:
                        update()
                    break;
                    case 1:
                        console.log("Not updating now")
                    break;
                }
            }
            console.log("Update check completed")
        })
    }

    // Download the update file
    const download = (downloadedFile) => {

        return new Promise((resolve, reject)=>{

            let response = https.get(urlzip, (res) => {

                console.log('statusCode:', res.statusCode);
                console.log('headers:', res.headers);

                res.pipe(downloadedFile);
                console.log("File downloaded")
                updateStatus = "File downloaded"

                // Animating the button to indicate success message
                updateLoading = "animated bounce is-success"
                setTimeout(()=>updateLoading = "", 2000)
                

            })
            
            response.on('error', (err) => {

                console.error("Error occured while downloading file: (Try again or maybe check your internet connection)\n", err)
                updateLoading = "animated shake faster is-danger"
                setTimeout(()=>updateLoading = "", 2000)
                reject(err)
            });

            response.on("close", ()=>{
                
                console.log("Downloading Completed")

                // Extracting downloaded files
                console.log("Extracting files")

                setTimeout(()=>{
                    let zip = new admZip(`${__dirname}/../update/update.zip`);
                    zip.extractAllTo(/*target path*/`${__dirname}/../update`, /*overwrite*/true);

                    console.log("File Extracted")
                    updateStatus = "File Extracted"

                    // fadeInfadeOut()
                    resolve("File extracted")

                }, 1600)
            })
        })
    }

    // Update processing
    const update = () => {
        
        updateLoading = "is-loading"
        
        try {fs.readdirSync(updateFolder)} 
        catch (err) {
            exec(`mkdir ${updateFolder}`, (err, stdout, stderr)=>{
                if (err) {
                    console.log("Update failed.\nMaybe the user doesn't have necessary persmission to write files in the disk")
                    throw err;
                }
                console.log(stdout)
                console.log("Update folder created")
            })
        }
        finally {

            setTimeout(()=>{
                const downloadedFile = fs.createWriteStream(zipFile);
                download(downloadedFile)
                    .then(result=>{
                        console.log(result)
                        console.log("Copying downloaded files")
                        let src = path.resolve(__dirname, "..", "update", `${github.repo}-${github.branch}`)
                        let dest = path.resolve(__dirname, "..")

                        copy(src, dest, {overwrite: true}, function(error, results) {
                            if (error) {
                                console.error('Copy failed: ' + error);
                                updateStatus = "Update failed.\nMaybe the user doesn't have necessary persmission to write files in the disk"
                            } else {
                                console.info('Copied ' + results.length + ' files');
                                updateStatus = "Updated succesfull. Restart the program (Press Ctrl + R)."
                                let response = showinfo(mainWindow, {title:"FELion_GUI2", type:"info", message:"Update succesfull", buttons:["Restart", "Restart later"]})
                                if (response===0) mainWindow.reload()
                            }
                        });
                    })
                    .catch(err=>console.log(err), updateStatus = "Update failed. Try again or Check your internet connection")
                
            }, 1000)
        }
        
    }

    // Checking for internet connection
    function checkInternet(cb) {

        require('dns').lookup('google.com',function(err) {
            if (err && err.code == "ENOTFOUND") {
                cb(false);
            } else {
                cb(true);
            }
        })
    }

    // Checking for update on startup
    checkInternet(function(isConnected) {
        isConnected ? updateCheck() : console.log("Internet is not connected")
    })

    // Checking for update on regular time interval
    const hr_ms = (time) => time*60*60*10**3
    let timeInterval = hr_ms(1)
    let check_update_continuously = setInterval(()=>{
        checkInternet(function(isConnected) {
            isConnected ? updateCheck() : console.log("Internet is not connected")
        })

        }, timeInterval
    )

</script>

<style>

    .is-active {
        background-color: #46307d!important;
        border-radius: 2em;
    }
    .menu-list a:hover {
        
        border-left: 2px solid;
        background-color: rgba(0,0,0,0)!important;
    }

    .label {
        font-size: 1.4rem;
        font-weight: 400;
    }
    .row {
        display: flex;
        flex-direction: column;
        padding-bottom: 2em;
    }

    .menu-label, label{
        color: #fafafa;
    }

    .menu-label {font-size: 1.6em;}

    .box2 {
        background-color: #4e348e;
        width: 70%;
    }

    .box {
        overflow-y: auto;
        max-height: 70vh;
        min-width: 20%;
        position: absolute;
    }

</style>

<section class="section animated fadeIn" style="display:none" id="Settings">

    <div class="columns">

        <div class="column is-3">
            <aside class="menu box" style="height:100%">
                
                <div class="menu-label">Settings</div>
                <ul class="menu-list">
                    {#each items as item}
                        <li><a class="menulist" on:click={toggle} id="{item}Container">{item}</a></li>
                    {/each}
                </ul>

            </aside>
        </div>

        <div class="column">
            <div class="row box box2" style="height:100%" >
                <div class="container is-fluid">

                    <!-- Configuration Settings -->

                    <div class="container" id="Configuration">

                        <!-- Python path -->
                        <div class="field">
                            <label class="label">PythonPath </label>
                            <div class="control">
                                <input class="input" type="text" placeholder="Enter the default python.exe file path" bind:value={pythonpath}>
                            </div>
                            <p class="help">location of python.exe file: to run python scripts</p>
                        </div>

                        <!-- Python script files -->
                        <div class="field">
                            <label class="label">Python Scripts </label>
                            <div class="control">
                                <input class="input" type="text" placeholder="Enter the default python.exe file path" bind:value={pythonscript}>
                            </div>
                            <p class="help">location of python script files</p>
                        </div>

                        <!-- Save changes button -->
                        <div class="control">
                            <button class="button is-link is-pulled-right" on:click={configSave}>Save</button>
                            <h1 class="subtitle animated {saveChangeanimate}" style="display:{saveChanges}">Changes saved!</h1>
                        </div>
                    </div>

                    <!-- Update -->

                    <div class="container" style="display:none" id="Update">
                        <div class="control">
                            <h1 class="title">FELion GUI (Current version): {currentVersion}</h1>
                            <button class="button is-warning is-pulled-right" on:click="{()=>mainWindow.reload()}">Restart</button>

                            <div class="level">
                                <div class="level-left">
                                    <div class="level-item">
                                        <button class="button is-link {checkupdateLoading}" on:click={updateCheck} >Check Update</button>
                                    </div>

                                    <div class="level-item" id="updatelabel" style="display:{updatetoggle}">
                                        <h1 class="subtitle">Version available: {new_version}</h1>
                                    </div>

                                    <div class="level-item" id="run_update" style="display:{updatetoggle}">
                                        <button class="button is-warning {updateLoading}" on:click={update}>Update</button>
                                    </div>

                                </div>
                            </div>
                            
                            <h1 class="subtitle" style="display:block">{updateStatus}</h1>
                            
                        </div>
                    </div>

                    <!-- About -->

                    <div class="container" style="display:none" id="About">
                        <div class="control">
                            <h1 class="title">Software details (version)</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Electron.js: {process.versions.electron}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Node.js: {process.versions.node}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Chrome: {process.versions.chrome}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">{pythonv}</h1>
                            <hr>
                            <h1 class="title">Javascript Frameworks and libraries</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Svelte.js: {packageJSON.devDependencies.svelte.split("^")[1]}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">jQuery: {packageJSON.dependencies["jquery"].split("^")[1]}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Typescript: {packageJSON.devDependencies.typescript.split("^")[1]}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Tippy.js: {packageJSON.dependencies["tippy.js"].split("^")[1]}</h1>
                            <hr>
                            <h1 class="title">CSS Frameworks and libraries</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Bulma: {packageJSON.devDependencies["bulma"].split("^")[1]}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Fontawesome: {packageJSON.devDependencies["@fortawesome/fontawesome-free"].split("^")[1]}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">pretty-checkbox: {packageJSON.dependencies["pretty-checkbox"].split("^")[1]}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">hover.css: {packageJSON.dependencies["hover.css"].split("^")[1]}</h1>
                            
                        </div>
                    </div>
                    
                </div>
            </div>
        </div>

    </div>
  
</section>