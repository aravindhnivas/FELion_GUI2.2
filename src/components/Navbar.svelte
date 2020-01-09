<script>
  export let navItems;
  export let jq;
  console.log("Loading");
  jq(document).ready(() => {
    jq("#Navbar").css("display", "block");
  });

  const controlNav = event => {

    let target = event.target.innerHTML;
    console.log(target + " is-active");

    navItems.forEach(item => { 
      let bgColor = window.navbarBgColor || "#5b3ea2"
      let $item = jq(`#${item}`), $itemParent = jq(`#${item}-nav`)
      
      if(item == target) {
        $item.css("display", "block")
        $itemParent.addClass("is-active").removeClass("non-active")
        jq(`#${item}-nav a`).css("background-color", bgColor)
      } else {
        $item.css("display", "none")
        $itemParent.addClass("non-active").removeClass("is-active")
        jq(`#${item}-nav a`).css("background-color", "transparent")
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
    /* background-color: #6046a0fc; */
  }
  .tabs.is-boxed a:hover {border: 1px solid white}
  
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
              <a on:click={controlNav} class="">{item}</a>
            </li>
          {:else}
            <li id="{item}-nav" class="non-active">
              <a on:click={controlNav} >{item}</a>
            </li>
          {/if}
        {/each}
      </ul>
    </div>
  </div>
</section>
