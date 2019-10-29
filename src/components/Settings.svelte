<script>

    export let jq;
    export let path;
    
    if (!localStorage["pythonpath"]) localStorage["pythonpath"] = path.join(__dirname, "../python3.7/python")
    if (!localStorage["pythonscript"]) localStorage["pythonscript"] = path.join(__dirname, "/python_files/")

    $: savebtn = {name:"Save", style:"is-link"}
    let pythonpath = localStorage["pythonpath"];
    let pythonscript = localStorage["pythonscript"];


    const configSave = () => {

        localStorage["pythonpath"] = pythonpath
        localStorage["pythonscript"] = pythonscript

        console.log(`Updated: \nPythonpath: ${localStorage.pythonpath}\nPython script: ${localStorage.pythonscript}`)
        savebtn = {name:"saved", style:"is-success"}

        setTimeout(()=>savebtn = {name:"Save", style:"is-link"}, 1000)
    }

</script>

<style>

    a.is-active {
        background-color: #46307d!important;

        border-radius: 2em;
    }
    .menu-list a:hover {
        
        border-radius:2em;
        background-color: #876dc7!important;
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
                    <li><a class="is-active">Configuration</a></li>
                    <li><a >About</a></li>
                </ul>

            </aside>
        </div>

        <div class="column">

            <div class="row box box2" style="height:100%" >
                <div class="container is-fluid">

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

                        <div class="control">
                            <button class="button {savebtn["style"]} is-pulled-right" on:click={configSave}>{savebtn["name"]}</button>
                        </div>
                    </div>
                    
                </div>
            </div>

            
        </div>

    </div>
  
</section>