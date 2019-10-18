<script>

    export let electron;
    export let path;
    export let jq;

    import * as fs from 'fs';

    const dialog = electron.remote.dialog;
    let currentLocation;

    let today = new Date();
    const dd = String(today.getDate()).padStart(2, '0');
    const mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    const yy = today.getFullYear().toString().substr(2);
    today = `${dd}_${mm}_${yy}-#`;

    $: filename = today+".pow";

    let fileContent = `#POWER file\n` +
        `# 10 Hz FELIX\n` +
        `#SHOTS=26\n` +
        `#INTERP=linear\n` +
        `#    IN_no_UM (if one deletes the no the firs number will be in \mu m\n` +
        `# wavelength/cm-1      energy/pulse/mJ\n`

    function browseFolder() {
        const options = {
            title: `Open a folder`,
            properties: ['openDirectory'],
            message: `Open a folder` //For macOS
        };
        dialog.showOpenDialog(null, options, (folder) => {
            if (folder==undefined) return console.log("No files selected");
            currentLocation = folder[0];
        });
    };


    const btnAnimate = (name, removeclass, addclass, timeout) =>{
        jq("#powSaveBtn").html(name).removeClass(removeclass).addClass(addclass);
        setTimeout(()=>{jq("#powSaveBtn").html("Save").removeClass(addclass).addClass(removeclass);}, timeout)
    };

    function powSave() { 

        if(currentLocation==undefined) {return btnAnimate("Browse folder first !!!", "is-link", "is-danger animated shake faster", 3000);}
        fs.writeFile(path.join(currentLocation, filename), fileContent, (err) => {

            btnAnimate("File saved", "is-link", "is-success animated bounce", 2000);
            if (err) throw err;
        }) };

</script>

<style>
.row {
    display: flex;
    flex-direction: column;
    padding-bottom: 2em;
}
#powerfileLocationLabel, #powfilename {text-align: center}
label {color: white}
.container {height: 70vh;}
.columns {height: 100%;}
#powfileContent_mainContainer {height: 70%;}
#powfileContent_Container {height: 90%;}
#powfileContents {height: 100%;}

/* Handle */
::-webkit-scrollbar-thumb {
    background: #3f3e3e; 
    border-radius: 10px;
}

/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
    background: #2222229d;
}

</style>

<section class="section" style="display:none" id="Powerfile">

    <div class="container">
        <div class="columns">
            <div class="column">

                <div class="field has-addons">
                    <div class="control is-expanded">
                        <input class="input locationLabel" type="text" 
                        placeholder="Location will be displayed" id="powerfileLocationLabel" 
                        bind:value={currentLocation}>
                    </div>
                    <div class="control">
                        <div class="button is-dark" on:click={browseFolder} data-tippy="Open a folder">Browse</div>
                    </div>
                </div>

                <div class="field">
                    <label class="label">Filename</label>
                    <div class="control">
                        <input class="input" type="text" placeholder="Filename" id="powfilename" bind:value={today}>
                    </div>
                </div>

                <div class="field" id="powfileContent_mainContainer">
                    <label class="label">File Contents</label>
                    <div class="control" id="powfileContent_Container">
                        <textarea class="textarea" placeholder="Textarea" id="powfileContents" bind:value={fileContent} 
                            on:keyup="{(e)=>{if(e.code=="Space"){fileContent = fileContent.substr(0, fileContent.length-1)+"\t"}}}"></textarea>
                    </div>
                </div>

                <div class="field">
                    <div class="control">
                        <button class="button is-link" id="powSaveBtn" on:click={powSave}>Save</button>
                    </div>
                </div>

            </div>
        </div>
    </div>

</section>