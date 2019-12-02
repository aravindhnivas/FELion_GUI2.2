<script>

  // Importing svelte components
  import Header from "./Header.svelte";
  import Navbar from "./Navbar.svelte";
  import Welcome from "./Welcome.svelte";
  import Container from "./Container.svelte";
  import Powerfile from "./Powerfile.svelte";
  import Settings from "./Settings.svelte"
  import Footer from "./Footer.svelte";
  import Misc from "./Misc.svelte"
  import { onMount } from 'svelte';

  // const copy = require('recursive-copy');
  // const { exec } = require("child_process");
  window.developerMode = false

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

  if (!localStorage["pythonpath"]) localStorage["pythonpath"] = path.resolve(__dirname, "..", "python3.7", "python")

  // Getting variables
  export let mainPages;
  const navItems = ["Welcome", "Normline", "Masspec", "Timescan", "THz", "Powerfile", "Misc", "Settings"];
 
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

  // let src = path.resolve(__dirname, "npmPackages")
  // let dest = path.resolve(__dirname, "../node_modules")

  // copy(src, dest, {overwrite: false}, function(error, results) {
  //     console.log(results)
  //     if (error) console.log('Copy failed: ' + error)
  //     else console.info('Copied ' + results.length + ' files')
  // })

  // let pipFilename = path.resolve(__dirname, "pipPackages", "streamlit-0.51.0-py2.py3-none-any.whl")
  // exec(`${localStorage.pythonpath} -m pip install ${pipFilename}`, (err, result)=>{
    
  //   if(err) {console.log(err)} 
  //   else {console.log(result)}
  // })

</script>

<Header {jq} />

<Navbar {navItems} {jq}/>
<Welcome {jq}/>

{#each mainPages as page}
  <Container {...page} {jq} {electron} {menu} {MenuItem} {path}/>
{/each}

<Powerfile {electron} {path} {jq}/>
<Settings {jq} {path} {mainWindow} {showinfo} {electron}/>
<Misc />
<Footer {jq}/>