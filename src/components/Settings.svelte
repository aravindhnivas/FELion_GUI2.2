<script>

    export let jq;
    export let path;
    export let mainWindow;
    export let showinfo;
    export let electron;

    import { fade, fly } from 'svelte/transition';

    import NewNav from "./utils/NewNav.svelte";
    import FrontBackNav from "./utils/FrontBackNav.svelte";


    // Importing modules
    const {exec} = require("child_process")
    const https = require('https');
    const fs = require('fs')
    const admZip = require('adm-zip');
    const copy = require('recursive-copy');

    jq(document).ready(()=>{

        jq("#PagesContainer").addClass("is-active")
        console.log(`Internet Status: ${navigator.onLine}`)
        if (navigator.onLine) updateCheck()
        else console.log("Internet is not connected.")
    })
    let packageJSON = fs.readFileSync(path.join(__dirname, "../package.json"))

    packageJSON = JSON.parse(packageJSON.toString("utf-8"))
    let versionFile = fs.readFileSync(path.join(__dirname, "../version.json"))
    let currentVersion = JSON.parse(versionFile.toString("utf-8")).version

    // Pythonpath and pythonscript files location
    
    if (!localStorage["pythonpath"]) localStorage["pythonpath"] = path.resolve(__dirname, "..", "python3.7", "python")
    if (!localStorage["pythonscript"]) localStorage["pythonscript"] = path.resolve(__dirname, "python_files")
    let pythonpath = localStorage["pythonpath"]
    let pythonscript = localStorage["pythonscript"]

    // Getting python version
    let pythonv;
    exec(`${pythonpath} -V`, (err, stdout, stderr)=>{
        pythonv = stdout
        console.log(`Python version: ${pythonv}`)

        if (pythonv === "") {
            let options = {
                title: "Incorrect Python path",
                message: "Python is not configured (or wrong python path is given)\nGo to 'Setting->Configuration->PythonPath'",
                type:"warning",
                buttons: ["Okay, I will change"],
            }
            showinfo(mainWindow, options)
            jq("#Welcome").css("display", "none")
            jq("#Welcome-nav").removeClass("is-active")
            jq("#Settings-nav").addClass("is-active")
            jq("#Settings").css("display", "block")
        }
    })

    function checkPython(){
        console.log("Python path: ", pythonpath)
        return new Promise((resolve, reject)=>{

            exec(`${pythonpath} -V`, (err, stdout, stderr)=>{
            let options = {
                title: "Incorrect Python path", message: `Python directory is not valid\n${pythonpath}`, type:"warning",
            }
            
            if(stdout==="") {
                showinfo(mainWindow, options)
                reject("Invalid pythonpath: ", pythonpath)
            } else { resolve("Valid pythonpath: ", pythonpath) }
            })
        })
    }
    // Pages in Settings

    let items = ["Pages", "Configuration", "Update", "About"]

    //////////////////////////////////////////////////// FUNCTIONS ////////////////////////////////////////////////////
    $: saveChanges = false

    const configSave = () => {
        checkPython().then(res=>{
            console.log(res)

            localStorage["pythonpath"] = pythonpath
            localStorage["pythonscript"] = pythonscript
            console.log(`Updated: \nPythonpath: ${localStorage.pythonpath}\nPython script: ${localStorage.pythonscript}`)
            saveChanges = true
        }).catch(err=>{console.log(err); pythonpath = localStorage["pythonpath"]})
        
    }
    const set_defaultConfig = () => {

        pythonpath = path.resolve(__dirname, "..", "python3.7", "python")

        checkPython().then(res=>{
            console.log(res)
            pythonpath = localStorage["pythonpath"] = path.resolve(__dirname, "..", "python3.7", "python")
            pythonscript = localStorage["pythonscript"] = path.resolve(__dirname, "python_files")
            saveChanges = true
        }).catch(err=>{ console.log(err); pythonpath = localStorage["pythonpath"] })
        
    }
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

    let github_username = "aravindhnivas"
    let github_repo = "FELion_GUI2.2"

    $: gihub_branchname = "master"
    $: console.log(`Branch changed: ${gihub_branchname}`)

    $: versionJson = `https://raw.githubusercontent.com/${github_username}/${github_repo}/${gihub_branchname}/version.json`
    $: urlzip = `https://codeload.github.com/${github_username}/${github_repo}/zip/${gihub_branchname}`

    // Local update-downloaded files
    const updateFolder = path.resolve(__dirname, "..", "update")
    const updatefilename = "update.zip"
    const zipFile = path.resolve(updateFolder, updatefilename)


    const updateCheck = () => {
        updatetoggle = "none"
        console.log("Checking for update")

        checkupdateLoading = "is-loading"
        let developer_version = false;
        console.log(`URL_Package: ${versionJson}`)

        console.log(`URL_ZIP: ${urlzip}`)

        let request = https.get(versionJson, (res) => {

            console.log('statusCode:', res.statusCode);
            console.log('headers:', res.headers);

            res.on('data', (data) => {

                data = data.toString("utf8")
                console.log(data)
                data = JSON.parse(data)
                console.log(data)
                new_version = data.version
                developer_version = data.developer

                console.log(`Developer version: ${developer_version}`)
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

            if (currentVersion === new_version) {
                if (developer_version) {
                    updateStatus = `CAUTION! You are checking with developer branch which has experimental features. Take backup before updating.`
                } else {updateStatus = `No stable update available.`}
            }
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

            setTimeout(()=>checkupdateLoading = "", 2000)
        })
    }

    // Download the update file
    const download = (downloadedFile) => {
        return new Promise((resolve, reject)=>{

            let response = https.get(urlzip, (res) => {
                console.log(`URL: ${urlzip}`)
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

    const update = () => {
        // archive()
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
                        let src = path.resolve(__dirname, "..", "update", `${github_repo}-${gihub_branchname}`)
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
                        })
                        
                    })
                    .catch(err=>console.log(err), updateStatus = "Update failed. Try again or Check your internet connection")
                
            }, 1000)
        }
        
    }

    // Checking for update on regular time interval
    const hr_ms = (time) => time*60*60*10**3
    let timeInterval_hr = 1

    let check_update_continuously;
    
    // Clock timer
    $: currentTime = ""
    function ClockTimer() {
        let date = new Date();
        currentTime = date.toLocaleTimeString();
    }
    let clock = setInterval(ClockTimer, 1000);

    // Auto update
    $: auto_update_check = true
    $: if (auto_update_check){ 
        console.log("Auto update On")
        let timeInterval = hr_ms(timeInterval_hr)

        console.log(`Auto update check for every ${timeInterval_hr} hr. (${timeInterval} ms)`)
        check_update_continuously = setInterval(()=>{
            checkInternet(function(isConnected) {isConnected ? updateCheck() : console.log("Internet is not connected")})
            }, timeInterval
        )
     } else {
        console.log("Auto update Off")
        clearInterval(check_update_continuously)
    }

    $: backupClass = "is-link"
    $: backupName = "FELion_GUI_backup"

    function openFolder() {
        return new Promise((resolve, reject) => {

            const options = {
                title: "Browse folder",
                properties: ["openDirectory"],
                message: "Browse folder" //For macOS

            }
            electron.remote.dialog.showOpenDialog(null, options, location => {
                location === undefined ? reject("No folder selected") : resolve(location[0])

            })
        })
    }

    $: back_restore_display = false;
    $: back_restore_log = ""

    const backup_restore_logIt = (str) => {

        back_restore_display = true
        back_restore_log = str

        setTimeout(()=>{back_restore_display = false}, 4000)
    }


    const archive = (event) => {

        backupClass = "is-loading is-link"

        console.log(`Archiving existing software to ${backupName}.zip`)

        openFolder()
        .then(location=>{

            let folderName = location

            console.log("Selected folder: ", folderName)

            let _src = {path:path.resolve(__dirname, "..", "src"), name:"src"}
            let _static = {path:path.resolve(__dirname, "..", "static"), name:"static"}
            let _dist = {path:path.resolve(__dirname, "..", "dist"), name:"dist"}
            let packageFile = {path:path.resolve(__dirname, "..", "package.json"), name:"package.json"}
            let rollup = {path:path.resolve(__dirname, "..", "rollup.config.js"), name:"rollup.config.js"}
            let tsconfig = {path:path.resolve(__dirname, "..", "tsconfig.json"), name:"tsconfig.json"}

            let folders = [_src, _dist, _static, packageFile, rollup, tsconfig]

            folders.forEach(folder=>{
                const _dest = path.resolve(folderName, backupName , folder.name)
                copy(folder.path, _dest, {overwrite: true}, function(error, results) {
                    if (error) {
                        console.log('Copy failed: ' + error);
                        
                    } else {
                        console.info('Copied ' + results.length + ' files')
                        console.info('Copied ' + results + ' files')
                        console.log("BackUp completed")
                        backup_restore_logIt("BackUp completed")
                    }
                })
                
            })

            backupClass = "is-success bounce"
            setTimeout(()=>backupClass = "is-link", 2000)
            
        })
        .catch(err=>{
            if (err != "No folder selected") {
                backupClass = "is-danger animated shake faster"
                setTimeout(()=>backupClass = "is-link", 2000)
                backup_restore_logIt("BackUp Failed !!!")
            } else {backupClass = "is-link"}
            
            console.log(err)
            
        })
    }

    $: restoreClass = "is-warning"

    const restore = () =>{
        restoreClass = "is-warning is-loading"
        console.log(`Restoring existing software to ${__dirname}`)
        openFolder()
        .then(location=>{

            let folderName = location

            console.log("Selected folder: ", folderName)

            let _src = {path:path.resolve(folderName, "src"), name:"src"}
            let _static = {path:path.resolve(folderName, "static"), name:"static"}
            let _dist = {path:path.resolve(folderName, "dist"), name:"dist"}
            let packageFile = {path:path.resolve(folderName, "package.json"), name:"package.json"}
            let rollup = {path:path.resolve(folderName, "rollup.config.js"), name:"rollup.config.js"}
            let tsconfig = {path:path.resolve(folderName, "tsconfig.json"), name:"tsconfig.json"}
            let folders = [_src, _dist, _static, packageFile, rollup, tsconfig]

            folders.forEach(folder=>{
                const _dest = path.resolve(__dirname, "..", folder.name)
                copy(folder.path, _dest, {overwrite: true}, function(error, results) {
                    if (error) {
                        console.log('Copy failed: ' + error);
                    } else {
                        console.info('Copied ' + results.length + ' files')
                        console.info('Copied ' + results + ' files')
                        console.log("Restoring completed")
                        backup_restore_logIt("Restoring completed")
                        let response = showinfo(mainWindow, {title:"FELion_GUI2", type:"info", message:"Restored succesfull", buttons:["Restart", "Restart later"]})
                        if (response===0) mainWindow.reload()
                        else console.log("Restarting later")
                    }
                })
                
            })

            restoreClass = "is-success bounce"
            setTimeout(()=>restoreClass = "is-warning", 2000)
            
        })
        .catch(err=>{

            if (err != "No folder selected") {
                restoreClass = "is-danger animated shake faster"
                setTimeout(()=>restoreClass = "is-warning", 2000)
                backup_restore_logIt("Restoring Failed !!!")
            } else {restoreClass = "is-warning"}
            console.log(err)
        })
    }
    
    $: developer_mode = false
    $: developer_mode ? window.developerMode = true : window.developerMode = false

    $: console.log("Developer mode: ", developer_mode)
    $: numberOfPages = 5
    $: pageName = _.range(numberOfPages+1).map(num=>`Page ${num}`)
    $: console.log(pageName)

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
        overflow-x: hidden;
        max-height: 70vh;
        min-width: 20%;
        position: absolute;
    }

    .title {font-weight: 400;}
    .subtitle {color: white;}

</style>

<section class="section animated fadeIn" style="display:none" id="Settings">

    <div class="columns">

        <div class="column is-3">
            <aside class="menu box" style="height:100%">
                
                <div class="menu-label">Settings</div>
                <ul class="menu-list">
                    {#each items as item, index}
                        <li><a class="menulist" on:click={toggle} id="{item}Container">{item}</a></li>
                    {/each}
                </ul>

            </aside>
        </div>

        <div class="column">
            <div class="row box box2" style="height:100%" >
                <div class="container is-fluid">
                    
                    <div class="is-pulled-right">{currentTime}</div>

                    <!-- Pages -->

                    <div class="container-fluid" id="Pages" style="display:block">
                        <!-- <NewNav {pageName} /> -->
                        <div class="container" id="Page 0" style="display:block">
                            <div class="control">
                                <h1 class="title">Page Configuration</h1>
                                <FrontBackNav id={"Page 0"} {pageName}/>
                            </div>

                            <div class="field">
                                <label class="label">Number of Pages</label>
                                <div class="control">
                                    <input type="number" class="input" bind:value={numberOfPages} min="1" id="numberOfPage" style="width:20%">
                                </div>
                            </div>
                            
                        </div>
                        
                        {#each pageName as id (id)}
                            <div class="container" {id} style="display:none">
                                <div class="control">
                                    <h1 class="title">{id}</h1>
                                    <FrontBackNav {id} {pageName}/>
                                </div>
                                <label class="label">Page Name</label>
                                <div class="control">
                                    <input type="text" class="input" value={id} id="{id}-name" style="width:20%">
                                </div>
                            </div>
                        {/each}
                    </div>
                    <!-- Configuration Settings -->
                    <div class="container" id="Configuration" style="display:none">

                        <!-- Python path -->
                        <div class="field">
                            <label class="label">PythonPath </label>
                            <div class="control">
                                <input class="input" type="text" placeholder="Enter the default python.exe file path" bind:value={pythonpath} on:change={configSave}>
                            </div>
                            <p class="help">location of python.exe file: to run python scripts</p>
                        </div>

                        <!-- Python script files -->
                        <div class="field">
                            <label class="label">Python Scripts </label>
                            <div class="control">
                                <input class="input" type="text" placeholder="Enter the default python.exe file path" bind:value={pythonscript} on:change={configSave}>
                            </div>
                            <p class="help">location of python script files</p>
                        </div>

                        <!-- Save changes button -->
                        <div class="level">
                            <div class="level-left">
                                <button class="level-item button is-warning" on:click={set_defaultConfig}>Set Defaults</button>
                                <button class="level-item button is-link" on:click={configSave}>Save</button>
                            </div>
                            <div class="level-right">
                                {#if saveChanges}
                                    <h1 class="level-item subtitle" transition:fade on:introend="{()=>setTimeout(() => saveChanges=false, 2000)}">Changes saved!</h1>
                                {/if}
                            </div>
                        </div>
                    
                        <div class="control">
                            <div class="pretty p-switch p-slim" style="margin:1em;" >
                                <input type="checkbox" bind:checked={developer_mode}/>
                                <div class="state p-info p-on">
                                    <label>Developer mode</label>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Update -->
                    <div class="container" style="display:none" id="Update">
                        
                        <h1 class="title">FELion GUI (Current version): {currentVersion}</h1>
                        <hr>
                        <div class="level">
                            <div class="level-left">
                                <div class="level-item"><input type="text" class="input" data-tippy="Github Username" bind:value={github_username}></div>
                                <div class="level-item"><input type="text" class="input" data-tippy="Github repo" bind:value={github_repo}></div>
                                <div class="level-item">
                                    <div class="select">
                                        <select bind:value={gihub_branchname}>
                                            <option>master</option>
                                            <option>developer</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <hr>
                        <div class="field is-grouped">
                            <p class="control"><button class="button is-link {checkupdateLoading}" on:click={updateCheck} >Check Update</button></p>
                            <p class="control"><button class="button is-warning {updateLoading}" on:click={update}>Update</button></p>
                        </div>
                        <h1 class="subtitle" style="display:block">{updateStatus}</h1>
                        
                        <hr>

                        <!-- Auto update options -->
                        <div class="pretty p-switch p-slim" style="margin-bottom:1em;">
                            <input type="checkbox" bind:checked={auto_update_check} id="autoupdate"/>
                            <div class="state p-info p-on">
                                <label>Auto update</label>
                            </div>
                        </div>

                        <div class="field has-addons">
                            <div class="control"><div class="button is-static">Time Interval (in hours)</div></div>
                            <div class="control">
                                <input type="number" class="input"
                                    placeholder="Enter update check for every (time in hrs) interval"
                                    value=1 on:change="{(e)=>timeInterval_hr = e.target.value}"
                                    data-tippy="Check for update every hour">
                            </div>
                        </div>

                        <hr>
                        <div class="field is-grouped">
                            <p class="control"><input type="text" class="input" bind:value={backupName} data-tippy="Backup folder name"></p>
                            <p class="control"><button class="button animated {backupClass}" on:click={archive} >Backup</button></p>
                            <p class="control"><button class="button animated {restoreClass}" on:click={restore} >Restore</button></p>
                            {#if back_restore_display}
                                <p class="control" transition:fade> {back_restore_log} </p>
                            {/if}
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
                            <h1 class="subtitle" style="margin-bottom:0">Bulma: {packageJSON.dependencies["bulma"].split("^")[1]}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Fontawesome: {packageJSON.dependencies["@fortawesome/fontawesome-free"].split("^")[1]}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">pretty-checkbox: {packageJSON.dependencies["pretty-checkbox"].split("^")[1]}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">hover.css: {packageJSON.dependencies["hover.css"].split("^")[1]}</h1>
                            
                        </div>
                    </div>
                    
                </div>
            </div>
        </div>

    </div>
  
</section>