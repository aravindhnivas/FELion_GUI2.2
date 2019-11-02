<script>
  export let navItems;
  export let jq;
  console.log("Loading");
  jq(document).ready(() => {
    jq("#Navbar").css("display", "block");
  });

  const displayToggle = (element, value, classname) => {
    let parent = (document.getElementById(
      element + "-nav"
    ).classList = classname);
    try {
      let targetElement = (document.getElementById(
        element
      ).style.display = value);
    } catch (err) {
      console.log(element + " Not yet created or Error loading the page.");
    }
  };

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

  const toggleRow = () => {
    jq(".locationRow").toggle();
    jq(".buttonsRow").toggle();
    let display = jq(".buttonsRow").css("display");
    display === "none"
      ? jq(".plotContainer").css("max-height", "75vh")
      : jq(".plotContainer").css("max-height", "60vh");
  };
</script>

<!-- Navigation Bar -->

<section class="section animated fadeInDown" id="Navbar" style="display:none">
  <div class="container is-fluid">
    <div class="tabs is-centered is-boxed is-medium">
      <span
        class="icon is-pulled-left"
        style="margin:0.5em; cursor:pointer"
        on:click={toggleRow}
        data-tippy="Show/Hide buttons">
        <i
          class="fas fa-bars fa-2x"
          style="padding:0.5em;"
          aria-hidden="true" />
      </span>
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
