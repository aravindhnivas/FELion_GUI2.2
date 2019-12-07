<script>
  export let navItems;
  export let jq;
  console.log("Loading");
  jq(document).ready(() => {
    jq("#Navbar").css("display", "block");
  });

  const displayToggle = (element, value, classname) => {

    let parent = (document.getElementById(element + "-nav").classList = classname)
    try {

      let targetElement = (document.getElementById(element).style.display = value)
    } catch (err) {
      console.log(element + " Not yet created or Error loading the page.");
    }
  }

  const controlNav = event => {

    let target = event.target.innerHTML;
    console.log(target + " is-active");

    navItems.forEach(item => {
      if (item == target) {
        displayToggle(item, "block", "is-active");
      } else {
        displayToggle(item, "none", "");
      }
    });
  };
  
</script>

<style>

  i:focus {outline-color: transparent;}
  #fullToggle {
    margin-left: 0.7em;
    margin-top: 0.7em;
    cursor:pointer;
  }

  .section {padding: 0.3rem}

  .tabs.is-medium {
    font-weight: lighter;
    font-size: 1.1rem;
  }
  .tabs {background: transparent}
  .tabs.is-boxed a {border-radius: 20px;}

  .tabs ul {
    border-bottom-style: none;
  }
  .tabs.is-boxed li.is-active a {
    border-color:transparent;
    background-color: #6046a0fc;
  }
  .tabs.is-boxed a:hover {background-color: #6046a0fc;}
  
  #Navbar {

    background-color: #4a3284;
    margin-bottom: 0;
    
  }


</style>

<!-- Navigation Bar -->

<section class="section box animated fadeInDown" id="Navbar" style="display:none">
  <div class="container is-fluid">
    <div class="tabs is-centered is-boxed is-medium">
      
      <ul>
        {#each navItems as item}
          {#if item == 'Welcome'}
            <li class="is-active" id="{item}-nav">
              <a on:click={controlNav}>{item}</a>
            </li>
          {:else}
            <li id="{item}-nav">
              <a on:click={controlNav}>{item}</a>
            </li>
          {/if}
        {/each}
      </ul>
    </div>
  </div>
</section>
