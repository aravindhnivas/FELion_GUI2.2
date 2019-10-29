<script>

    export let jq;
    export let path;
    
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

</script>

<style>

    .is-active {
        background-color: #46307d!important;
        border-radius: 2em;
    }
    .menu-list a:hover {
        
        border-radius:2em;
        background-color: #46307d!important;
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
                            <h1 class="subtitle">FELion GUI (Current version): {localStorage.version}</h1>
                            <div class="level">
                                <div class="level-left">
                                    <div class="level-item">
                                        <button class="button is-link" >Check Update</button>
                                    </div>

                                    <div class="level-item" id="updatelabel" style="display:none">
                                        <h1 class="subtitle">Version available: </h1>
                                    </div>

                                    <div class="level-item" id="run_update" style="display:none">
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