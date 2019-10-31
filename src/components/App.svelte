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

<Settings {jq} {path} {mainWindow} {showinfo}/>

<Footer {jq}/>