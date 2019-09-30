<script>
  import Header from "./Header.svelte";
  import Navbar from "./Navbar.svelte";
  import Welcome from "./Welcome.svelte";
  import Container from "./Container.svelte";
  import Powerfile from "./Powerfile.svelte";
  import Footer from "./Footer.svelte";

  import tippy from 'tippy.js'; //For tooltip
  import * as jQuery from 'jquery';
  import * as electron from 'electron';
  import * as path from 'path';

  const jq = jQuery.default;

  // Getting variables
  export let mainPages;

  const navItems = ["Welcome", "Normline", "Masspec", "Timescan", "THz", "Powerfile"];

</script>

<Header />

<Navbar {navItems}/>

<Welcome />

{#each mainPages as { id, filetag, filetype, funcBtns, plotID }}
  <Container {id} {filetag} {filetype} {funcBtns} {plotID} {jq} {electron} {path}/>
{/each}
<Powerfile {electron} {path} {jq}/>
<Footer/>