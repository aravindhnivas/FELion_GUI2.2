<script>
    const urlOpen = (url) => {
      let modal = window.open(url, 'modal')
    }

    const websites_row1 = [
      {
        url: "http://www.colby.edu/chemistry/PChem/Hartree.html",
        name: "Boltzman Population"
      },
      {
        url: "http://halas.rice.edu/conversions",
        name: "Unit Conversion"
      }
    ]
    $: loadURL = "http://www.colby.edu/chemistry/PChem/Hartree.html"

</script>

<style>
  .row {
    display: flex;
    flex-direction: column;
    padding-bottom: 2em;
  }

  #webpage {height: 70vh;}

  webview {
    height: 90%;
    background: #e8e8e8;
  }

</style>

<section class="section animated fadeIn" style="display:none" id="Misc">

  <div class="columns is-centered is-multiline">

    <div class="column box is-11">
      <div class="level">
        <div class="level-left">

          {#each websites_row1 as {url, name}}
            <div class="level-item">
              <button class="button is-link" 
                data-tippy={url} 
                on:click="{()=>loadURL = url}">
                {name}
              </button>
            </div>
          {/each}

        </div>
      </div>
    </div>

    <div class="column box is-11" id="webpage">
      <div class="field">
        <div class="control">
          <input class="input is-primary" type="text" placeholder="type Webaddress" 
            value={loadURL} 
            on:keyup="{(e)=>{if (e.key=="Enter") loadURL= `https://www.${e.target.value}`}}">
        </div>
      </div>
      <webview src={loadURL} nodeintegration></webview>

    </div>
  </div>
</section>