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

  // const toggleRow = () => {

  //   jq(".locationRow").toggle();
  //   jq(".buttonsRow").toggle();
  //   jq(".filebrowserColumn").toggle();

  //   let display = jq(".buttonsRow").css("display");

  //   if (display === "none"){

  //     jq(".plotContainer").css("max-height", "75vh")
  //     jq(".plotContainer").css("width", "97%")

  //   } 
  //   else {
  //     jq(".plotContainer").css("max-height", "60vh");
  //     jq(".plotContainer").css("width", "81%")

  //   }
    
  //   let obj = { width: jq(".plotContainer").width() * 0.97 };
  //   Plotly.relayout("saPlot", obj);
  //   Plotly.relayout("bplot", obj);
  //   Plotly.relayout("avgplot", obj);

  //   Plotly.relayout("exp-theory-plot", obj);
  //   Plotly.relayout("mplot", obj);
  // };

</script>

<style>

  i:focus {outline-color: transparent;}
  #fullToggle {

    margin-left: 0.7em;
    margin-top: 0.7em;
    cursor:pointer;
  }

</style>

<!-- Navigation Bar -->

<section class="section animated fadeInDown" id="Navbar" style="display:none">
  <div class="container is-fluid">
    <div class="tabs is-centered is-boxed is-medium">
      <!-- <span
        class="icon is-pulled-left"
        on:click={toggleRow} id="fullToggle"
        >
        <i
          class="fas fa-bars fa-2x"
          style="padding:0.5em;"
          aria-hidden="true" data-tippy="Show/Hide layout" data-tippy-placement="right-start" data-tippy-arrow="true"/>
      </span> -->
      
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
