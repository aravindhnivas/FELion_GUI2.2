<script>

  // Importing svelte components
  import Header from "./Header.svelte";
  import Navbar from "./Navbar.svelte";
  import Welcome from "./Welcome.svelte";
  import Container from "./Container.svelte";
  import Powerfile from "./Powerfile.svelte";
  import Settings from "./Settings.svelte"
  import Footer from "./Footer.svelte";

  // Importing other modules
  import tippy from 'tippy.js'; //For tooltip
  import * as jQuery from 'jquery';
  import * as electron from 'electron';
  import * as path from 'path';

  const fs = require("fs")
  const https = require('https');

  const jq = jQuery.default;
  const remote = electron.remote
  const mainWindow = remote.getCurrentWindow()
  const Menu = remote.Menu
  const MenuItem = remote.MenuItem
  const showinfo = remote.dialog.showMessageBox

  let current_version = fs.readFileSync(path.join(__dirname, "../package.json"))
  current_version = JSON.parse(current_version.toString("utf-8")).version
  localStorage["version"] = current_version

  const github = {
        username: "aravindhnivas",
        repo: "FELion_GUI2.2",
        branch: "master",
    }

  $: updateNow = false

  $: console.log("Update now: ", updateNow)

  const urlPackageJson = `https://raw.githubusercontent.com/${github.username}/${github.repo}/${github.branch}/package.json`
  let request = https.get(urlPackageJson, (res) => {

                  console.log("Checking for update")

                  res.on('data', (data) => {
                    data = JSON.parse(data.toString("utf8"))
                    let new_version = data.version
                    console.log("Available version: ", new_version)
                    if (current_version === new_version) {
                      let options = {
                        title: "FELion_GUI2",
                        message: "Update available "+new_version,
                        buttons: ["Update and restart", "Cancel"],
                        type:"info"

                      }
                      let response = showinfo(mainWindow, options)
                      console.log(response)
                      switch (response) {
                        case 0:
                          localStorage.setItem("updateNow", "true")
                          updateNow = true
                          break;
                        case 1:
                          localStorage.setItem("updateNow", "false")
                          updateNow = false
                          break;
                      }
                    }
                  })

                })

  request.on("error", (err)=>console.log("Error occured while checiking for update"))
  request.on("close", ()=>console.log("Update check done"))

  // Getting variables
  export let mainPages;
  const navItems = ["Welcome", "Normline", "Masspec", "Timescan", "THz", "Powerfile", "Settings"];
 
  let rightClickPosition = null
  const menu = new Menu()

  menu.append(new MenuItem({ label: 'cut', role:"cut" }))
  menu.append(new MenuItem({ label: 'copy', role:"copy" }))
  menu.append(new MenuItem({ label: 'paste', role:"paste" }))

  menu.append(new MenuItem({ type: 'separator' }))

  menu.append(new MenuItem({ label: 'Reload', role:"reload" }))
  menu.append(new MenuItem({ label: 'DevTools', role: 'toggledevtools' }))
  menu.append(new MenuItem({ label: "Inspect Element", click() { remote.getCurrentWindow().inspectElement(rightClickPosition.x, rightClickPosition.y) } }))
  menu.append(new MenuItem({ type: 'separator' }))

  
  window.addEventListener('contextmenu', (e) => {
      e.preventDefault()
      rightClickPosition = {x: e.x, y: e.y}
      menu.popup(remote.getCurrentWindow())
    }, false)

</script>

<Header {jq} />

<Navbar {navItems} {jq}/>

<Welcome {jq}/>

{#each mainPages as { id, filetag, filetype, funcBtns, plotID, checkBtns}}
  <Container {id} {filetag} {filetype} {funcBtns} {plotID} {checkBtns} {jq} {electron} {menu} {MenuItem} {path}/>
{/each}
<Powerfile {electron} {path} {jq}/>

<Settings {jq} {path} {mainWindow} {updateNow} {showinfo}/>

<Footer {jq}/>