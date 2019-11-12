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

    const editmode_constants = () => {

      let fundamental_constants = Array.from(document.getElementsByClassName("fun.constants"))
      let status = document.getElementById("edit_constants").checked
      fundamental_constants.forEach(input => input.disabled = !status)
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
          <input class="input" type="number" bind:value={hz} target="hz">Hz
          <input class="input" type="number" bind:value={um} target="um" on:change="{()=>hz=(c/um)*1e6}">&mu;m
          <input class="input" type="number" bind:value={cm_1} target="cm_1" on:change="{()=>hz=cm_1*c*1e2}">cm-1
          <input class="input" type="number" bind:value={kelvin} target="kelvin" on:change="{()=>hz=(boltzman_constant/plank_constant)*kelvin}">K
          <input class="input" type="number" bind:value={eV} target="eV" on:change="{()=>hz=(electron_charge/plank_constant)*eV}">eV

          <hr>
          <h1 class="subtitle is-pulled-left">Fundamental constants</h1>
          <div class="pretty p-switch p-slim is-pulled-right" on:click={editmode_constants}>
              <input type="checkbox" id="edit_constants"/>
              <div class="state p-info p-on">
                  <label>Edit</label>
              </div>
          </div>
          <input class="input fun.constants" type="number" disabled bind:value={c} data-tippy="Speed of light in vaccum">m/s
          <input class="input fun.constants" type="number" disabled bind:value={boltzman_constant} data-tippy="Boltzman constant">J/K
          <input class="input fun.constants" type="number" disabled bind:value={plank_constant} data-tippy="Plank's constant">J.s
          <input class="input fun.constants" type="number" disabled bind:value={electron_charge} data-tippy="Electric charge">Columb

        </div>
        
      </div>
    </div>

  </div>
</section>