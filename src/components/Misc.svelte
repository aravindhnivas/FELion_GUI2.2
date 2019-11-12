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

    // Fundamental constants

    $: c = 299792458 // m/s
    $: plank_constant = 6.62607004e-34 // Js
    $: boltzman_constant = 1.380649e-23 // J/K
    $: electron_charge = 1.602176565e-19 // C or eV = J

    // eV/q = h.c/lam = h.f = KB.T = h.c.cm_1

    $: hz = 100;
    $: eV = (plank_constant/electron_charge) * hz;
    $: kelvin = (plank_constant/boltzman_constant) * hz;
    $: cm_1 = hz/(c*1e2);
    $: um = (c/hz)*1e+6;
    const energy_list = ["hz", "um", "kelvin", "cm_1", "eV"]

    const energy_conversion = {

      hz:{
        cm_1: (freq) => freq/(c*1e2),
        eV: (freq) => (plank_constant/electron_charge) * freq,
        kelvin: (freq) => (plank_constant/boltzman_constant) * freq,
        um: (freq) => (c/freq)*1e+6
      },
      cm_1:{
        hz: (cm_1) => cm_1 * 1e-2 * c,
        eV: (cm_1) => (plank_constant*c*electron_charge) * cm_1 * 1e-2,
        kelvin: (cm_1) => (plank_constant/boltzman_constant) * c * cm_1 * 1e-2,
        um: (cm_1) => 1e4/cm_1
      }
    }

    const convert = (e) => {

      let target = e.target.getAttribute("target")
      console.log(target)
      let value = e.target.value
      let fn = energy_conversion[target]

      switch (target) {

        case "hz":

          cm_1 = fn.cm_1(value)
          eV = fn.eV(value)
          um = fn.um(value)
          kelvin = fn.kelvin(value)

          break;

        case "cm_1":

          hz = fn.hz(value)
          eV = fn.eV(value)
          um = fn.um(value)
          kelvin = fn.kelvin(value)

          break;
      
        default:
          break;
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
    height: 70vh;
  }
  .input {
    margin-right: 0.5em;
    margin-bottom: 0.5em;
    width: 75%
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

    <div class="column is-11 page animated fadeIn" id="Converter" style="display:block;">

      <div class="columns is-multiline" id="unit_conversion_table">

        <div class="column {table_sz}">

          <h1 class="title">Energy Conversion</h1>
          <input class="input" type="number" bind:value={hz} target="hz" on:keyup={convert}>Hz
          <input class="input" type="number" bind:value={um} target="um" on:keyup={convert}>&mu;m
          <input class="input" type="number" bind:value={cm_1} target="cm_1" on:keyup={convert}>cm-1
          <input class="input" type="number" bind:value={kelvin} target="kelvin" on:keyup={convert}>K
          <input class="input" type="number" bind:value={eV} target="eV" on:keyup={convert}>eV

          <hr>
          <h1 class="subtitle is-pulled-left">Fundamental constants</h1>
          <div class="pretty p-switch p-slim is-pulled-right">
              <input type="checkbox" id="edit_constants"/>
              <div class="state p-info p-on">
                  <label>Edit</label>
              </div>
          </div>
          <input class="input" type="number" bind:value={c} data-tippy="Speed of light in vaccum">m/s
          <input class="input" type="number" bind:value={boltzman_constant} data-tippy="Boltzman constant">J/K
          <input class="input" type="number" bind:value={plank_constant} data-tippy="Plank's constant">J.s
          <input class="input" type="number" bind:value={electron_charge} data-tippy="Electric charge">Columb

        </div>
        
      </div>
    </div>

  </div>
</section>