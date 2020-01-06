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

  $: hz = 1e12;
  $: eV = (plank_constant/electron_charge) * hz;
  $: kelvin = (plank_constant/boltzman_constant) * hz;
  $: cm_1 = hz/(c*1e2);
  $: um = (c/hz)*1e+6;
  $: ghz = hz*1e-9
  $: nm = (c/hz)*1e+9
  $: J = plank_constant * hz
  
  $: edit_constants = false

  $: edit_numberDensity_constants = false

  // Number density

  $: pq1_before = 1e-8
  $: pq1_after = 1e-5
  $: ptrap_before = 1e-10
  $: ptrap_after = 1e-5
  $: temperature = 5
  $: calibration_factor = 205.54

  $: rt = 300

  $: ndensity_temp = calibration_factor/(boltzman_constant*1e4*rt**0.5) * ((pq1_after - pq1_before) / temperature**0.5)
  $: ndensity = ndensity_temp.toExponential(4)

</script>

<style lang="scss">

  $link-color: #dbdbdb;
  $link-hovercolor: #7a64b1;

  .button.is-link {border-color: $link-color; background-color: rgba(0,0,0,0);}
  .button.is-link:hover, .button.is-link.is-hovered {background-color: $link-hovercolor;}
  .button.is-link:focus:not(:active), .button.is-link.is-focused:not(:active) {box-shadow: 0 0 0 0.05em #fafafa;}
  .page {height: 70vh;}

  .conversion_table {
    margin-right: 0.5em;
    height: 70vh;
  }
  .energy {
    margin-right: 0.5em;
    margin-bottom: 0.5em;
    width: 75%
  }

  .label {
    color: #fafafa;
    font-weight: 400;
  }
  input {margin-bottom: 0.5em;}
  .subtitle {color: white;}

  .unit_converter_column {
    overflow: auto;
  }

</style>

<section class="section animated fadeIn" style="display:none" id="Misc">

  <div class="columns is-centered is-multiline animated fadeIn">

    <!-- Navigator Row -->

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

    <!-- Unit Converter Page -->

    <div class="column is-11 page animated fadeIn" id="Converter" style="display:block;">

      <div class="columns is-multiline" id="unit_conversion_table">

        <div class="column {table_sz} unit_converter_column">
          <h1 class="title">Energy Conversion</h1>

          <hr>
          <input class="input energy" type="number" bind:value={hz} >Hz
          <input class="input energy" type="number" bind:value={ghz} on:change="{()=>hz=(ghz)*1e+9}" target="hz">GHz
          <input class="input energy" type="number" bind:value={um} on:change="{()=>hz=(c/um)*1e6}">&mu;m
          <input class="input energy" type="number" bind:value={cm_1} on:change="{()=>hz=cm_1*c*1e2}">cm-1
          <input class="input energy" type="number" bind:value={kelvin} on:change="{()=>hz=(boltzman_constant/plank_constant)*kelvin}">K
          <input class="input energy" type="number" bind:value={eV} on:change="{()=>hz=(electron_charge/plank_constant)*eV}">eV
          <input class="input energy" type="number" bind:value={J} on:change="{()=>hz=(J/plank_constant)}">J
          <input class="input energy" type="number" bind:value={nm} on:change="{()=>hz=(c/nm)*1e9}">nm

          <hr>

          <h1 class="subtitle is-pulled-left">Fundamental constants</h1>
          <div class="pretty p-switch p-slim is-pulled-right">
              <input type="checkbox" bind:checked={edit_constants}/>
              <div class="state p-info p-on">
                  <label>Edit</label>
              </div>
          </div>
          <input class="input fun.constants energy" type="number" disabled={!edit_constants} bind:value={c} data-tippy="Speed of light in vaccum">m/s
          <input class="input fun.constants energy" type="number" disabled={!edit_constants} bind:value={boltzman_constant} data-tippy="Boltzman constant">J/K
          <input class="input fun.constants energy" type="number" disabled={!edit_constants} bind:value={plank_constant} data-tippy="Plank's constant">J.s
          <input class="input fun.constants energy" type="number" disabled={!edit_constants} bind:value={electron_charge} data-tippy="Electric charge">Columb

        </div>

        <div class="column {table_sz} unit_converter_column">
          
          <h1 class="title">Number Density Calculation</h1>

          <hr>

          <div class="columns is-multiline">

            <div class="column is-half">
              <div class="field">
                <label class="label">Main Chamber Press.</label>
                <div class="control">
                  <input class="input ndensity" bind:value={pq1_before} type="number" step="0.000000001" placeholder="Before" data-tippy="Before letting in gas">
                  <input class="input ndensity" bind:value={pq1_after} type="number" step="0.000000001" placeholder="After" data-tippy="After letting in gas">
                </div>
              </div>
            </div>

            <div class="column is-half">
              <div class="field">
                <label class="label">Temperature</label>
                <div class="control">
                  <input class="input ndensity" bind:value={temperature} type="number"  placeholder="Temeprature">
                </div>
              </div>
            </div>
            
            <div class="column is-half">
              <div class="field">
                <label class="label">Number density</label>
                <div class="control">
                  <button class="button is-static">{ndensity}</button>
                </div>
              </div>
            </div>

          </div>

          <hr>

          <div class="control">
            <h1 class="subtitle is-pulled-left">Constants</h1>
            <div class="pretty p-switch p-slim is-pulled-right">
                <input type="checkbox" bind:checked={edit_numberDensity_constants}/>
                <div class="state p-info p-on">
                    <label>Edit</label>
                </div>
            </div>
          </div>
          
          <div class="control">

            <div class="field">
              <label class="label">Calibration Factor</label>
              <div class="control">
                <input class="input number_constants" bind:value={calibration_factor} type="number" placeholder="Number density" disabled={!edit_numberDensity_constants}>
              </div>
            </div>

            <div class="field">
              <label class="label">Chamber Temperature (RT)</label>
              <div class="control">
                <input class="input number_constants" bind:value={rt} type="number" step="0.1" placeholder="Number density" disabled={!edit_numberDensity_constants}>
              </div>
            </div>

          </div>
          
        </div>
        
      </div>
    </div>

  </div>
</section>