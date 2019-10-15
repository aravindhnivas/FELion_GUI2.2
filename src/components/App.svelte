<script>

  // Importing svelte components
  import Header from "./Header.svelte";
  import Navbar from "./Navbar.svelte";
  import Welcome from "./Welcome.svelte";
  import Container from "./Container.svelte";
  import Powerfile from "./Powerfile.svelte";
  import Footer from "./Footer.svelte";

  // Importing other modules
  import tippy from 'tippy.js'; //For tooltip
  import * as jQuery from 'jquery';
  import * as electron from 'electron';
  import * as path from 'path';
  const jq = jQuery.default;

  // Getting variables
  export let mainPages;
  const navItems = ["Welcome", "Normline", "Masspec", "Timescan", "THz", "Powerfile"];
 
  const remote = electron.remote
  const Menu = remote.Menu
  const MenuItem = remote.MenuItem

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

<Header />

<Navbar {navItems}/>

<Welcome {jq}/>

{#each mainPages as { id, filetag, filetype, funcBtns, plotID, checkBtns}}
  <Container {id} {filetag} {filetype} {funcBtns} {plotID} {checkBtns} {jq} {electron} {menu} {MenuItem} {path}/>
{/each}
<Powerfile {electron} {path} {jq}/>
<Footer/>