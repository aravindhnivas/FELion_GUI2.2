<script>
  export let navItems;

  const displayToggle = (element, value, classname) => {
    let parent = document.getElementById(element+"-nav").classList = classname
    try {let targetElement = document.getElementById(element).style.display = value;}
    catch (err) {console.log(element+" Not yet created or Error loading the page.")}
  }

  const controlNav = event => {

    let target = event.target.innerHTML;

    console.log(target+" is-active")

    navItems.forEach(item => {
      if (item == target) {displayToggle(item, "block", "is-active")} 
      else {displayToggle(item, "none", "")} 
    });
  };
</script>

<!-- Navigation Bar -->

<section class="section" id="Navbar">
  <div class="container is-fluid">
    <div class="tabs is-centered is-boxed is-medium">
      <ul>
        {#each navItems as item}
          {#if item=="Welcome"}
            <li class="is-active" id="{item}-nav" ><a on:click={controlNav}>{item}</a></li>
          {:else}
            <li id="{item}-nav"><a on:click={controlNav}>{item}</a></li>
          {/if}
        {/each}
      </ul>
    </div>
  </div>
</section>