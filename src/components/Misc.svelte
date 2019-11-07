<script>
    const pages = ["Converter", "Internet"]
    const navigator = [
      {
        name: "Unit Converter",
        target: "Converter",
        id: "unit_converter_navbtn"
      },
      {
        name: "Internet",
        target: "Internet",
        id:"internet_navbtn"
      }
    ]
    
    const toggler = (event) => {

      let target_id = event.target.getAttribute("target")

      let target = document.getElementById(target_id)
      target.style.display = "block"
      pages.filter(page=> page != target_id).forEach(page=>document.getElementById(page).style.display="none")
    }

</script>

<style>

  .page {height: 70vh;}
</style>

<section class="section animated fadeIn" style="display:none" id="Misc">
  <div class="columns is-centered is-multiline">

    <div class="column box is-11">
      <div class="level">
        <div class="level-left">
          {#each navigator as {name, target}}
            <div class="level-item">
              <button class="button is-link misc_btn" {target} on:click={toggler} >
                {name}
              </button>
            </div>
          {/each}
        </div>
      </div>
    </div>

    <div class="column box is-11 page" id="Converter" style="display:block;">Converter</div>
    <div class="column box is-11 page" id="Internet" style="display:none;">Internet</div>

  </div>
</section>