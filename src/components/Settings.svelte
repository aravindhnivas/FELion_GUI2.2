<script>

    export let jq;
    export let path;
    
    const https = require('https');
    const fs = require('fs');

    jq(document).ready(()=>{jq("#ConfigurationContainer").addClass("is-active")})

    if (!localStorage["pythonpath"]) localStorage["pythonpath"] = path.join(__dirname, "../python3.7/python")
    if (!localStorage["pythonscript"]) localStorage["pythonscript"] = path.join(__dirname, "/python_files/")

    let pythonpath = localStorage["pythonpath"];
    let pythonscript = localStorage["pythonscript"];

    let items = ["Configuration", "Update", "About"]
    $: saveChanges = "none"
    $: saveChangeanimate = "fadeIn"

    const fadeInfadeOut = () => {

        saveChanges = "block"
        setTimeout(()=>saveChangeanimate="fadeOut", 1200)
        setTimeout(()=>{
            saveChangeanimate = "fadeIn"
            saveChanges = "none"
        }, 2000)
    }

    const configSave = () => {

        localStorage["pythonpath"] = pythonpath
        localStorage["pythonscript"] = pythonscript

        console.log(`Updated: \nPythonpath: ${localStorage.pythonpath}\nPython script: ${localStorage.pythonscript}`)
        fadeInfadeOut()

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
            } 
            else {

                $element.addClass("is-active")
                targetElement.style.display = "block"
            }
        })
    }

    $: new_version = ""
    $: updatetoggle = "none"

    $: checkupdateLoading = ""

    const update = () => {

        updatetoggle = "none"
        console.log("Checking for update")
        checkupdateLoading = "is-loading"


        https.get('https://raw.githubusercontent.com/aravindhnivas/FELion_GUI2.2/master/package.json', (res) => {

            console.log('statusCode:', res.statusCode);
            console.log('headers:', res.headers);
            res.on('data', (data) => {

                // process.stdout.write(data);
                data = JSON.parse(data.toString("utf8"))

                new_version = data.version
                console.log(`Received package:`, data)
                console.log(`Version available ${new_version}`)
                console.log(`Current version ${localStorage.version}`)
                
                updatetoggle = "block"
                checkupdateLoading = "animated bounce is-success"
                setTimeout(()=>checkupdateLoading = "", 2000)

                console.log("Completed")
            });

        }).on('error', (err) => {
            console.error("Error occured: (Try again or maybe check your internet connection)\n", err)
            checkupdateLoading = "animated shake faster is-danger"
            setTimeout(()=>checkupdateLoading = "", 2000)
        });

        
    }

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
                            <h1 class="title">FELion GUI (Current version): {localStorage.version}</h1>
                            <div class="level">
                                <div class="level-left">
                                    <div class="level-item">
                                        <button class="button is-link {checkupdateLoading}" on:click={update} >Check Update</button>
                                    </div>

                                    <div class="level-item" id="updatelabel" style="display:{updatetoggle}">
                                        <h1 class="subtitle">Version available: {new_version}</h1>
                                    </div>

                                    <div class="level-item" id="run_update" style="display:{updatetoggle}">
                                        <button class="button is-warning" >Update</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- About -->

                    <div class="container" style="display:none" id="About">
                        <div class="control">
                            <h1 class="title">Software details (version)</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Electron: {process.versions.electron}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Node: {process.versions.node}</h1>
                            <h1 class="subtitle" style="margin-bottom:0">Chrome: {process.versions.chrome}</h1>
                        </div>
                    </div>
                    
                </div>
            </div>
        </div>

    </div>
  
</section>