<script>
    const pages = ["Converter"]

    const navigator = [
      {
        name: "Unit Converter",
        target: "Converter",
        id: "unit_converter_navbtn"
      }
    ]
    
    const toggler = (event) => {
      let target_id = event.target.getAttribute("target")
      let target = document.getElementById(target_id).style.display = "block"
      pages.filter(page=> page != target_id).forEach(page=>document.getElementById(page).style.display="none")
    }

    $: table_sz  = "is-3 box conversion_table"

    const c = 299792458 //m/s
    $: hz = 1
    $: cm_1 = c/hz
    $: um = 0
    $: ev = 0
    $: kelvin = 0

    $: energy_input = "eg., 1 cm in um"

    const energy_conversion = {
      hz:{
        cm_1: 0,
        eV: (x) => 4.1356655385381e-15 * x,
        kelvin: 0,
        um: 0
      }
    }

    function convert_energy() {
      console.log(`Input received: ${energy_input}`)
      let formula = energy_input.split(" ")
      console.log(formula)

      let from_data = parseFloat(formula[0])
      let from = formula[1];
      let to = formula[3];
      let conversion_fn = energy_conversion[from][to]

      let to_data = conversion_fn(from_data)
      console.log(`Converted: ${to_data}`)
    }

</script>

<style>

  .page {height: 70vh;}
  .conversion_table {
    margin-right: 0.5em;
    height: 30vh;
  }
  .input {
    margin-right: 0.5em;
    margin-bottom: 0.5em;
    width: 70%
  }
</style>

<section class="section animated fadeIn" style="display:none" id="Misc">
  <div class="columns is-centered is-multiline animated fadeIn">

    <div class="column box is-11">
      <div class="level">
        <div class="level-left">
          {#each navigator as {name, target}}
            <div class="level-item">
              <button class="button is-link misc_btn" {target} on:click={toggler}>{name}</button>
            </div>
          {/each}
        </div>
      </div>
    </div>

    <div class="column is-11 page animated fadeIn" id="Converter" style="display:none;">

      <div class="columns is-multiline" id="unit_conversion_table">

        <div class="column {table_sz}">
          <h1 class="title">Energy Conversion</h1>
          <input class="input" type="text" bind:value={energy_input} on:keyup="{(e)=>{if (e.key === "Enter") convert_energy()}}">
          <!-- <input class="input" type="number" bind:value={hz}>Hz
          <input class="input" type="number" bind:value={um}>&mu;m
          <input class="input" type="number" bind:value={cm_1}>cm-1
          <input class="input" type="number" bind:value={kelvin}>K -->

        </div>
        
      </div>
    </div>

  </div>
</section>